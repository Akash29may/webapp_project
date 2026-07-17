from django.db import models

from courses.models import Course
from students.models import Student
from teachers.models import Teacher


class Exam(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.SET_NULL, null=True, blank=True, related_name="exams"
    )
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="exams")
    title = models.CharField(max_length=200)
    duration_min = models.PositiveIntegerField(default=30)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title

    @property
    def total_marks(self) -> int:
        return sum(q.marks for q in self.questions.all())


class Question(models.Model):
    MCQ = "mcq"
    SUBJECTIVE = "subjective"
    QTYPE_CHOICES = [(MCQ, "MCQ"), (SUBJECTIVE, "Subjective")]
    DIFFICULTY_CHOICES = [("easy", "Easy"), ("medium", "Medium"), ("hard", "Hard")]

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="questions")
    qtype = models.CharField(max_length=12, choices=QTYPE_CHOICES, default=MCQ)
    text = models.TextField()
    marks = models.PositiveIntegerField(default=1)
    difficulty = models.CharField(max_length=6, choices=DIFFICULTY_CHOICES, default="medium")
    model_answer = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self) -> str:
        return f"[{self.qtype}] {self.text[:50]}"


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices")
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.text


class ExamAttempt(models.Model):
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    AUTO_SUBMITTED = "auto_submitted"
    STATUS_CHOICES = [
        (IN_PROGRESS, "In progress"),
        (SUBMITTED, "Submitted"),
        (AUTO_SUBMITTED, "Auto submitted"),
    ]

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="attempts")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="attempts")
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    score = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=IN_PROGRESS)
    focus_warnings = models.PositiveIntegerField(default=0)
    gap_analysis = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ("exam", "student")

    def __str__(self) -> str:
        return f"{self.student} @ {self.exam} ({self.status})"

    @property
    def is_open(self) -> bool:
        return self.status == self.IN_PROGRESS


class Answer(models.Model):
    attempt = models.ForeignKey(ExamAttempt, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(
        Choice, on_delete=models.SET_NULL, null=True, blank=True
    )
    text_response = models.TextField(blank=True, null=True)
    awarded_marks = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    ai_rationale = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ("attempt", "question")

    def __str__(self) -> str:
        return f"Answer to Q{self.question_id} in attempt {self.attempt_id}"
