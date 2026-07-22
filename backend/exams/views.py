from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView

from ai import services as ai_services
from ai.models import AIEvaluationLog
from core.permissions import IsStudent, IsTeacher

from .models import Answer, Choice, Exam, ExamAttempt, Question
from .serializers import (
    ExamSerializer,
    PublishedExamSerializer,
    QuestionSerializer,
    QuestionTakeSerializer,
)


# ============================ Teacher: authoring ============================
class ExamViewSet(viewsets.ModelViewSet):
    serializer_class = ExamSerializer
    permission_classes = [IsTeacher]

    def get_queryset(self):
        return Exam.objects.filter(teacher=self.request.user.teacher)

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user.teacher)


class QuestionViewSet(viewsets.ModelViewSet):
    serializer_class = QuestionSerializer
    permission_classes = [IsTeacher]

    def get_queryset(self):
        return Question.objects.filter(exam__teacher=self.request.user.teacher)

    def perform_create(self, serializer):
        exam = get_object_or_404(
            Exam, pk=self.kwargs["exam_pk"], teacher=self.request.user.teacher
        )
        serializer.save(exam=exam)


class GenerateQuestionsView(APIView):
    permission_classes = [IsTeacher]

    def post(self, request, exam_pk):
        exam = get_object_or_404(Exam, pk=exam_pk, teacher=request.user.teacher)
        source_text = request.data.get("source_text", "")
        count = request.data.get("count", 3)
        qtypes = request.data.get("qtypes", ["mcq"])
        difficulty = request.data.get("difficulty", "medium")
        if not source_text:
            return Response(
                {"detail": "source_text is required."}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            questions = ai_services.generate_questions(source_text, count, qtypes, difficulty)
        except ai_services.LLMError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)
        AIEvaluationLog.objects.create(
            kind="generation",
            provider=request.data.get("_provider", ""),
            model="",
            prompt=source_text[:2000],
            response=str(questions)[:4000],
        )
        # Return DRAFTS (not saved); teacher reviews then POSTs them.
        return Response({"questions": questions})


class ExamResultsView(APIView):
    permission_classes = [IsTeacher]

    def get(self, request, exam_pk):
        exam = get_object_or_404(Exam, pk=exam_pk, teacher=request.user.teacher)
        attempts = []
        for a in exam.attempts.select_related("student__user"):
            attempts.append(
                {
                    "id": a.id,
                    "student_name": a.student.user.get_full_name() or a.student.user.username,
                    "score": a.score,
                    "total": exam.total_marks,
                    "status": a.status,
                    "submitted_at": a.submitted_at,
                    "focus_warnings": a.focus_warnings,
                }
            )
        return Response({"attempts": attempts})


# ============================ Student: exam engine ==========================
def _seconds_remaining(attempt: ExamAttempt) -> int:
    total = attempt.exam.duration_min * 60
    elapsed = (timezone.now() - attempt.started_at).total_seconds()
    return max(0, int(total - elapsed))


class PublishedExamListView(APIView):
    permission_classes = [IsStudent]

    def get(self, request):
        exams = Exam.objects.filter(is_published=True).select_related("teacher__user")
        return Response(PublishedExamSerializer(exams, many=True).data)


class StartAttemptView(APIView):
    permission_classes = [IsStudent]

    def post(self, request, exam_pk):
        exam = get_object_or_404(Exam, pk=exam_pk, is_published=True)
        attempt, _ = ExamAttempt.objects.get_or_create(
            exam=exam, student=request.user.student
        )
        return Response({"attempt_id": attempt.id}, status=status.HTTP_201_CREATED)


class AttemptStateView(APIView):
    permission_classes = [IsStudent]

    def get(self, request, pk):
        attempt = get_object_or_404(ExamAttempt, pk=pk, student=request.user.student)
        questions = attempt.exam.questions.prefetch_related("choices")
        answers = {
            str(a.question_id): {
                "selected_choice": a.selected_choice_id,
                "text_response": a.text_response,
            }
            for a in attempt.answers.all()
        }
        return Response(
            {
                "id": attempt.id,
                "exam_title": attempt.exam.title,
                "status": attempt.status,
                "seconds_remaining": _seconds_remaining(attempt),
                "questions": QuestionTakeSerializer(questions, many=True).data,
                "answers": answers,
            }
        )


class SaveAnswerView(APIView):
    permission_classes = [IsStudent]

    def patch(self, request, pk):
        attempt = get_object_or_404(ExamAttempt, pk=pk, student=request.user.student)
        if not attempt.is_open:
            return Response(
                {"detail": "Attempt already submitted."}, status=status.HTTP_400_BAD_REQUEST
            )
        question = get_object_or_404(
            Question, pk=request.data.get("question_id"), exam=attempt.exam
        )
        answer, _ = Answer.objects.get_or_create(attempt=attempt, question=question)
        choice_id = request.data.get("choice_id")
        if choice_id is not None:
            answer.selected_choice = get_object_or_404(
                Choice, pk=choice_id, question=question
            )
        if "text_response" in request.data:
            answer.text_response = request.data.get("text_response")
        answer.save()
        return Response({"saved": True})


class SubmitAttemptView(APIView):
    permission_classes = [IsStudent]

    @transaction.atomic
    def post(self, request, pk):
        attempt = get_object_or_404(
            ExamAttempt.objects.select_for_update(), pk=pk, student=request.user.student
        )
        exam = attempt.exam
        if not attempt.is_open:
            # Idempotent: return the already-computed result.
            return Response(
                {"score": attempt.score, "total": exam.total_marks, "status": attempt.status}
            )

        past_deadline = _seconds_remaining(attempt) <= 0
        answers = {a.question_id: a for a in attempt.answers.all()}
        total_score = 0
        weak = []

        for question in exam.questions.prefetch_related("choices"):
            answer = answers.get(question.id)
            if answer is None:
                weak.append((question, 0))
                continue
            if question.qtype == Question.MCQ:
                awarded = (
                    question.marks
                    if answer.selected_choice and answer.selected_choice.is_correct
                    else 0
                )
                answer.awarded_marks = awarded
                answer.save(update_fields=["awarded_marks"])
            else:  # subjective -> AI scoring
                try:
                    awarded, rationale, raw = ai_services.score_subjective(
                        question.text, question.model_answer or "",
                        answer.text_response or "", question.marks,
                    )
                except ai_services.LLMError:
                    awarded, rationale = 0, "AI scoring unavailable."
                answer.awarded_marks = awarded
                answer.ai_rationale = rationale
                answer.save(update_fields=["awarded_marks", "ai_rationale"])
                AIEvaluationLog.objects.create(
                    attempt=attempt, answer=answer, kind="subjective_score",
                    provider="", model="", prompt=question.text[:1000],
                    response=str(rationale)[:2000], score=awarded,
                )
            total_score += float(answer.awarded_marks or 0)
            if float(answer.awarded_marks or 0) < question.marks:
                weak.append((question, answer.awarded_marks))

        attempt.score = total_score
        attempt.status = (
            ExamAttempt.AUTO_SUBMITTED if past_deadline else ExamAttempt.SUBMITTED
        )
        attempt.submitted_at = timezone.now()

        # Gap analysis (#47)
        if weak:
            summary = "; ".join(
                f"'{q.text[:60]}' ({q.difficulty}) scored {m}/{q.marks}" for q, m in weak
            )
            try:
                attempt.gap_analysis = ai_services.analyze_gaps(summary)
                AIEvaluationLog.objects.create(
                    attempt=attempt, kind="gap_analysis", provider="", model="",
                    prompt=summary[:2000], response=(attempt.gap_analysis or "")[:2000],
                )
            except ai_services.LLMError:
                attempt.gap_analysis = ""
        attempt.save()
        return Response(
            {"score": attempt.score, "total": exam.total_marks, "status": attempt.status}
        )


class WarnView(APIView):
    permission_classes = [IsStudent]

    def post(self, request, pk):
        attempt = get_object_or_404(ExamAttempt, pk=pk, student=request.user.student)
        attempt.focus_warnings += 1
        attempt.save(update_fields=["focus_warnings"])
        return Response({"focus_warnings": attempt.focus_warnings})


class AttemptResultView(APIView):
    permission_classes = [IsStudent]

    def get(self, request, pk):
        attempt = get_object_or_404(ExamAttempt, pk=pk, student=request.user.student)
        answers = {a.question_id: a for a in attempt.answers.all()}
        questions = []
        for q in attempt.exam.questions.prefetch_related("choices"):
            answer = answers.get(q.id)
            correct_choice = next((c.id for c in q.choices.all() if c.is_correct), None)
            questions.append(
                {
                    "id": q.id,
                    "qtype": q.qtype,
                    "text": q.text,
                    "marks": q.marks,
                    "awarded_marks": answer.awarded_marks if answer else 0,
                    "your_choice": answer.selected_choice_id if answer else None,
                    "correct_choice": correct_choice,
                    "your_text": answer.text_response if answer else None,
                    "model_answer": q.model_answer,
                    "ai_rationale": answer.ai_rationale if answer else None,
                }
            )
        return Response(
            {
                "score": attempt.score,
                "total": attempt.exam.total_marks,
                "status": attempt.status,
                "gap_analysis": attempt.gap_analysis,
                "questions": questions,
            }
        )
