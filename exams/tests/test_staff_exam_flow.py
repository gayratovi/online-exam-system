from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from exams.models import Exam, ExamQuestion, StudentExamAttempt, StudentAnswer
from questions.models import Question
from accounts.models import Module

User = get_user_model()


class StaffExamFlowTests(TestCase):
    def setUp(self):
        # Create module
        self.module = Module.objects.create(code="CS101", name="Intro to CS")

        # Create staff user tied to this module
        self.staff = User.objects.create_user(
            username="alice",
            email="alice@csss.com",
            password="Staff1234!",
            role="staff",
            module=self.module
        )

        # Create student enrolled in same module
        self.student = User.objects.create_user(
            username="CSSS251001",
            email="csss251001@csss.com",
            password="Stu1234!",
            role="student",
        )
        self.student.modules.add(self.module)

    def login_staff(self):
        self.client.login(username="alice", password="Staff1234!")

    def create_exam(self):
        """Helper: create exam quickly"""
        now = timezone.now()
        return Exam.objects.create(
            title="Sample Exam",
            description="Test exam flow",
            module=self.module,
            is_active=True,
            opens_at=now - timedelta(hours=1),
            closes_at=now + timedelta(hours=1),
            duration_minutes=60,
        )

    def test_staff_can_create_exam(self):
        self.login_staff()
        response = self.client.post(reverse("create_exam"), {
            "title": "Midterm",
            "description": "Midterm test",
            "opens_at": (timezone.now() - timedelta(hours=1)).isoformat(),
            "closes_at": (timezone.now() + timedelta(days=1)).isoformat(),
            "duration_minutes": 60,
        })
        # Should redirect to manage-questions
        exam = Exam.objects.first()
        self.assertRedirects(response, reverse("staff_exam_questions_manage", args=[exam.id]))
        self.assertEqual(exam.title, "Midterm")

    def test_staff_can_add_question(self):
        self.login_staff()
        exam = self.create_exam()

        response = self.client.post(reverse("staff_exam_questions_manage", args=[exam.id]), {
            "question_text": "2+2?",
            "question_type": "FILL",
            "correct_answer": "4"
        })
        self.assertRedirects(response, reverse("staff_exam_questions_manage", args=[exam.id]))
        self.assertEqual(ExamQuestion.objects.filter(exam=exam).count(), 1)

    def test_staff_can_delete_question(self):
        self.login_staff()
        exam = self.create_exam()
        q = Question.objects.create(
            question_text="3+5?",
            question_type="FILL",
            module=self.module,
            correct_answer="8"
        )
        eq = ExamQuestion.objects.create(exam=exam, question=q)

        response = self.client.get(reverse("staff_exam_question_delete", args=[exam.id, q.id]))
        self.assertRedirects(response, reverse("staff_exam_questions_manage", args=[exam.id]))
        self.assertFalse(ExamQuestion.objects.filter(id=eq.id).exists())

    def test_results_overview_and_detail(self):
        self.login_staff()
        exam = self.create_exam()
        q = Question.objects.create(
            question_text="2+2?",
            question_type="FILL",
            module=self.module,
            correct_answer="4"
        )
        ExamQuestion.objects.create(exam=exam, question=q)

        # Student attempt (completed)
        attempt = StudentExamAttempt.objects.create(student=self.student, exam=exam, completed=True, score=100)
        StudentAnswer.objects.create(attempt=attempt, question=q, selected_answer="4", is_correct=True)

        # Staff overview
        response = self.client.get(reverse("staff_results_overview"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sample Exam")

        # Exam results view
        response = self.client.get(reverse("staff_exam_results", args=[exam.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Completed")

        # Question stats
        response = self.client.get(reverse("staff_exam_question_stats", args=[exam.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "2+2?")

        # Attempt detail
        response = self.client.get(reverse("staff_attempt_detail", args=[exam.id, attempt.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "2+2?")

    def test_export_csv(self):
        self.login_staff()
        exam = self.create_exam()
        attempt = StudentExamAttempt.objects.create(student=self.student, exam=exam, completed=True, score=90)

        response = self.client.get(reverse("staff_exam_results_export_csv", args=[exam.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")
        self.assertIn(f"exam_{exam.id}_results.csv", response["Content-Disposition"])
