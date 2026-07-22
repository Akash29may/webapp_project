from django.db import models


class AIEvaluationLog(models.Model):
    """Audit trail for AI generation, subjective scoring, and gap analysis."""

    KIND_CHOICES = [
        ("generation", "Generation"),
        ("subjective_score", "Subjective score"),
        ("gap_analysis", "Gap analysis"),
    ]

    attempt = models.ForeignKey(
        "exams.ExamAttempt",
        on_delete=models.CASCADE,
        related_name="ai_logs",
        null=True,
        blank=True,
    )
    answer = models.ForeignKey(
        "exams.Answer", on_delete=models.CASCADE, null=True, blank=True
    )
    kind = models.CharField(max_length=20, choices=KIND_CHOICES)
    provider = models.CharField(max_length=50)
    model = models.CharField(max_length=100)
    prompt = models.TextField(blank=True)
    response = models.TextField(blank=True)
    score = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.kind} ({self.provider}/{self.model})"
