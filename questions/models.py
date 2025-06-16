from django.db import models
from accounts.models import Module

class Question(models.Model):
    QUESTION_TYPES = (
        ('MCQ', 'Multiple Choice'),
        ('TF', 'True/False'),
        ('FILL', 'Fill in the Gap'),
    )

    question_text = models.TextField()
    question_type = models.CharField(max_length=4, choices=QUESTION_TYPES)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)

    # For MCQ only
    option_a = models.CharField(max_length=255, blank=True, null=True)
    option_b = models.CharField(max_length=255, blank=True, null=True)
    option_c = models.CharField(max_length=255, blank=True, null=True)
    option_d = models.CharField(max_length=255, blank=True, null=True)

    # For all types
    correct_answer = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.question_text} [{self.question_type}]"
