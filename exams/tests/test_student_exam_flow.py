from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from exams.models import Exam, ExamQuestion, StudentExamAttempt, StudentAnswer
from questions.models import Question
from accounts.models import Module

User = get_user_model()


class StudentExamFlowTests(TestCase):
    def setUp(self):
        # Create module
        self.module = Module.objects.create(code="CS101", name="Intro to CS")

        # Create student and enroll in module
        self.student = User.objects.create_user(
            username="CSSS251001",
            email="csss251001@csss.com",
            password="Stu1234!",
            role="student",
        )
        self.student.modules.add(self.module)

        # Exam (open now)
        now = timezone.now()
        self.exam = Exam.objects.create(
            title="Sample Exam",
            description="Test exam flow",
            module=self.module,
            is_active=True,
            opens_at=now - timedelta(hours=1),
            closes_at=now + timedelta(hours=1),
            duration_minutes=60,
        )

        # Two simple fill-in questions
        self.q1 = Question.objects.create(
            question_text="2+2?",
            question_type="FILL",
            module=self.module,
            correct_answer="4"
        )
        self.q2 = Question.objects.create(
            question_text="3+5?",
            question_type="FILL",
            module=self.module,
            correct_answer="8"
        )
        ExamQuestion.objects.create(exam=self.exam, question=self.q1)
        ExamQuestion.objects.create(exam=self.exam, question=self.q2)

    def login_student(self):
        self.client.login(username="CSSS251001", password="Stu1234!")

    def test_full_exam_flow_correct_answers(self):
        """Student takes exam and answers everything correctly."""
        self.login_student()

        # Start exam
        self.client.post(reverse("take_exam_start", args=[self.exam.id]))

        # Q1 → use correct_answer normalized
        self.client.post(
            reverse("take_exam_question", args=[self.exam.id, 0]),
            {"answer": self.q1.correct_answer.lower(), "next": "Next"}
        )

        # Q2 → use correct_answer normalized, submit
        response = self.client.post(
            reverse("take_exam_question", args=[self.exam.id, 1]),
            {"answer": self.q2.correct_answer.lower(), "submit": "Submit"}
        )
        self.assertRedirects(
            response,
            reverse("submit_exam", args=[self.exam.id]),
            fetch_redirect_response=False
        )

        # Submit exam → result
        response = self.client.post(reverse("submit_exam", args=[self.exam.id]))
        self.assertRedirects(response, reverse("exam_result", args=[self.exam.id]))

        # DB checks
        attempt = StudentExamAttempt.objects.get(student=self.student, exam=self.exam)
        self.assertTrue(attempt.completed)
        self.assertEqual(StudentAnswer.objects.filter(attempt=attempt).count(), 2)
        self.assertEqual(float(attempt.score), 100.00)

    def test_full_exam_flow_wrong_answers(self):
        """Student takes exam and gets everything wrong (score = 0)."""
        self.login_student()

        # Start exam
        self.client.post(reverse("take_exam_start", args=[self.exam.id]))

        # Q1 → wrong
        self.client.post(
            reverse("take_exam_question", args=[self.exam.id, 0]),
            {"answer": "wrong1", "next": "Next"}
        )

        # Q2 → wrong, submit
        response = self.client.post(
            reverse("take_exam_question", args=[self.exam.id, 1]),
            {"answer": "wrong2", "submit": "Submit"}
        )
        self.assertRedirects(
            response,
            reverse("submit_exam", args=[self.exam.id]),
            fetch_redirect_response=False
        )

        # Submit exam → result
        response = self.client.post(reverse("submit_exam", args=[self.exam.id]))
        self.assertRedirects(response, reverse("exam_result", args=[self.exam.id]))

        # DB check: score = 0
        attempt = StudentExamAttempt.objects.get(student=self.student, exam=self.exam)
        self.assertTrue(attempt.completed)
        self.assertEqual(float(attempt.score), 0.00)
