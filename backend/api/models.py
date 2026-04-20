from django.db import models
from django.contrib.auth.models import User


class Question(models.Model):
    """Questão cadastrada pelo professor, contendo enunciado e rubrica de correção."""
    title = models.CharField(max_length=255, verbose_name="Título")
    description = models.TextField(
        help_text="Enunciado completo da questão.",
        verbose_name="Enunciado",
    )
    rubric = models.TextField(
        help_text="Orientação do professor para a IA. O que se espera na resposta ideal.",
        verbose_name="Rubrica",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Questão"
        verbose_name_plural = "Questões"

    def __str__(self):
        return self.title


class Submission(models.Model):
    """Resposta submetida por um aluno a uma questão específica."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='submissions',
        null=True,
        blank=True,
        help_text="Nullable durante o MVP (sem autenticação).",
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='submissions',
    )
    answer_text = models.TextField(
        help_text="O texto escrito pelo aluno.",
        verbose_name="Resposta",
    )
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = "Submissão"
        verbose_name_plural = "Submissões"

    def __str__(self):
        return f"Submissão #{self.pk} — {self.question.title}"


class Feedback(models.Model):
    """Feedback gerado pela IA para uma submissão."""
    submission = models.OneToOneField(
        Submission,
        on_delete=models.CASCADE,
        related_name='feedback',
    )
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Nota",
    )
    constructive_feedback = models.TextField(verbose_name="Feedback Construtivo")
    key_strengths = models.TextField(verbose_name="Pontos Fortes")
    areas_for_improvement = models.TextField(verbose_name="Pontos a Melhorar")
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Feedback"
        verbose_name_plural = "Feedbacks"

    def __str__(self):
        return f"Feedback #{self.pk} — Nota {self.score}"
