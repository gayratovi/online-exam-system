from django.db import models
from django.utils import timezone
from questions.models import Question
from accounts.models import Module, CustomUser

class Exam(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)

    opens_at = models.DateTimeField(null=True, blank=True)
    closes_at = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(default=60)

    def __str__(self):
        return self.title

    def is_open_now(self):
        now = timezone.now()
        if self.opens_at and now < self.opens_at:
            return False
        if self.closes_at and now >= self.closes_at:
            return False
        return True

class ExamQuestion(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.exam.title} - {self.question.question_text[:50]}"

class StudentExamAttempt(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    ends_at = models.DateTimeField(null=True, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.student.username} - {self.exam.title}"

    # Helpers:
    def remaining_seconds(self):
        if not self.ends_at:
            return None
        return max(0, int((self.ends_at - timezone.now()).total_seconds()))

    def is_time_over(self):
        return bool(self.ends_at and timezone.now() >= self.ends_at)

class StudentAnswer(models.Model):
    attempt = models.ForeignKey(StudentExamAttempt, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.attempt.student.username} - Q: {self.question.id} - Ans: {self.selected_answer}"
