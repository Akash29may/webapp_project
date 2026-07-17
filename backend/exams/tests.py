from rest_framework.test import APITestCase

from core.tests import register
from exams.models import Exam, ExamAttempt, Question
from students.models import Student
from teachers.models import Teacher


def make_mcq(text="Q?", correct_index=0, marks=1):
    choices = [{"text": f"opt{i}", "is_correct": i == correct_index} for i in range(4)]
    return {"qtype": "mcq", "text": text, "marks": marks, "difficulty": "easy", "choices": choices}


class ExamAuthoringTests(APITestCase):
    def setUp(self):
        register(self.client, role="teacher", username="teach")
        self.teacher = Teacher.objects.get(user__username="teach")

    def test_teacher_creates_exam_and_mcq(self):
        exam = self.client.post("/api/exams/", {"title": "Quiz", "duration_min": 10})
        self.assertEqual(exam.status_code, 201, exam.data)
        exam_id = exam.data["id"]
        q = self.client.post(f"/api/exams/{exam_id}/questions/", make_mcq(), format="json")
        self.assertEqual(q.status_code, 201, q.data)
        self.assertEqual(Question.objects.count(), 1)

    def test_mcq_requires_four_choices_one_correct(self):
        exam = self.client.post("/api/exams/", {"title": "Quiz", "duration_min": 10})
        bad = make_mcq()
        bad["choices"] = bad["choices"][:3]
        resp = self.client.post(
            f"/api/exams/{exam.data['id']}/questions/", bad, format="json"
        )
        self.assertEqual(resp.status_code, 400)

    def test_student_cannot_author(self):
        self.client.post("/api/auth/logout/")
        register(self.client, role="student", username="stud")
        resp = self.client.post("/api/exams/", {"title": "X", "duration_min": 5})
        self.assertEqual(resp.status_code, 403)

    def test_ai_generation_returns_drafts(self):
        exam = self.client.post("/api/exams/", {"title": "Quiz", "duration_min": 10})
        resp = self.client.post(
            f"/api/exams/{exam.data['id']}/generate/",
            {"source_text": "Photosynthesis basics", "count": 2, "qtypes": ["mcq"]},
            format="json",
        )
        self.assertEqual(resp.status_code, 200, resp.data)
        self.assertEqual(len(resp.data["questions"]), 2)
        # drafts are NOT saved
        self.assertEqual(Question.objects.count(), 0)


class ExamEngineTests(APITestCase):
    def setUp(self):
        # teacher builds a published 1-MCQ exam
        register(self.client, role="teacher", username="teach")
        exam = self.client.post("/api/exams/", {"title": "Quiz", "duration_min": 10})
        self.exam_id = exam.data["id"]
        self.client.post(
            f"/api/exams/{self.exam_id}/questions/", make_mcq(correct_index=0, marks=5),
            format="json",
        )
        self.client.patch(
            f"/api/exams/{self.exam_id}/", {"is_published": True}, format="json"
        )
        self.correct_choice = Question.objects.first().choices.get(is_correct=True)
        self.wrong_choice = Question.objects.first().choices.filter(is_correct=False).first()
        self.client.post("/api/auth/logout/")
        register(self.client, role="student", username="stud")

    def test_published_list_visible_to_student(self):
        resp = self.client.get("/api/student/exams/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]["total_marks"], 5)

    def test_take_state_hides_answer_key(self):
        attempt = self.client.post(f"/api/exams/{self.exam_id}/attempt/")
        state = self.client.get(f"/api/attempts/{attempt.data['attempt_id']}/")
        self.assertEqual(state.status_code, 200)
        self.assertIn("seconds_remaining", state.data)
        choices = state.data["questions"][0]["choices"]
        for c in choices:
            self.assertNotIn("is_correct", c)  # answer key must NOT leak

    def test_correct_answer_scores_full_marks(self):
        attempt_id = self.client.post(f"/api/exams/{self.exam_id}/attempt/").data["attempt_id"]
        q_id = Question.objects.first().id
        self.client.patch(
            f"/api/attempts/{attempt_id}/answer/",
            {"question_id": q_id, "choice_id": self.correct_choice.id}, format="json",
        )
        result = self.client.post(f"/api/attempts/{attempt_id}/submit/")
        self.assertEqual(result.status_code, 200)
        self.assertEqual(float(result.data["score"]), 5.0)
        self.assertEqual(result.data["total"], 5)

    def test_wrong_answer_scores_zero(self):
        attempt_id = self.client.post(f"/api/exams/{self.exam_id}/attempt/").data["attempt_id"]
        q_id = Question.objects.first().id
        self.client.patch(
            f"/api/attempts/{attempt_id}/answer/",
            {"question_id": q_id, "choice_id": self.wrong_choice.id}, format="json",
        )
        result = self.client.post(f"/api/attempts/{attempt_id}/submit/")
        self.assertEqual(float(result.data["score"]), 0.0)

    def test_submit_is_idempotent(self):
        attempt_id = self.client.post(f"/api/exams/{self.exam_id}/attempt/").data["attempt_id"]
        self.client.post(f"/api/attempts/{attempt_id}/submit/")
        second = self.client.post(f"/api/attempts/{attempt_id}/submit/")
        self.assertEqual(second.status_code, 200)

    def test_autosave_then_resume_restores_answer(self):
        attempt_id = self.client.post(f"/api/exams/{self.exam_id}/attempt/").data["attempt_id"]
        q_id = Question.objects.first().id
        self.client.patch(
            f"/api/attempts/{attempt_id}/answer/",
            {"question_id": q_id, "choice_id": self.correct_choice.id}, format="json",
        )
        state = self.client.get(f"/api/attempts/{attempt_id}/")
        self.assertEqual(state.data["answers"][str(q_id)]["selected_choice"], self.correct_choice.id)

    def test_warn_increments_focus_warnings(self):
        attempt_id = self.client.post(f"/api/exams/{self.exam_id}/attempt/").data["attempt_id"]
        resp = self.client.post(f"/api/attempts/{attempt_id}/warn/")
        self.assertEqual(resp.data["focus_warnings"], 1)

    def test_student_cannot_access_others_attempt(self):
        attempt_id = self.client.post(f"/api/exams/{self.exam_id}/attempt/").data["attempt_id"]
        self.client.post("/api/auth/logout/")
        register(self.client, role="student", username="other")
        resp = self.client.get(f"/api/attempts/{attempt_id}/")
        self.assertEqual(resp.status_code, 404)


class SubjectiveGradingTests(APITestCase):
    def test_subjective_answer_ai_scored(self):
        register(self.client, role="teacher", username="teach")
        exam = self.client.post("/api/exams/", {"title": "Essay", "duration_min": 10})
        self.client.post(
            f"/api/exams/{exam.data['id']}/questions/",
            {
                "qtype": "subjective", "text": "Explain X", "marks": 10,
                "difficulty": "hard", "model_answer": "X is ...",
            },
            format="json",
        )
        self.client.patch(f"/api/exams/{exam.data['id']}/", {"is_published": True}, format="json")
        self.client.post("/api/auth/logout/")
        register(self.client, role="student", username="stud")
        attempt_id = self.client.post(f"/api/exams/{exam.data['id']}/attempt/").data["attempt_id"]
        q_id = Question.objects.first().id
        self.client.patch(
            f"/api/attempts/{attempt_id}/answer/",
            {"question_id": q_id, "text_response": "My essay answer"}, format="json",
        )
        result = self.client.post(f"/api/attempts/{attempt_id}/submit/")
        # mock provider returns 0.8 ratio -> 8/10
        self.assertEqual(float(result.data["score"]), 8.0)
        review = self.client.get(f"/api/attempts/{attempt_id}/result/")
        self.assertIsNotNone(review.data["gap_analysis"])
        self.assertEqual(review.data["questions"][0]["model_answer"], "X is ...")
