from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from accounts.models import Module
from exams.models import Exam
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class PermissionsTests(TestCase):
    def setUp(self):
        self.module = Module.objects.create(code="CS101", name="Intro to CS")

        # Staff user (single module FK)
        self.staff = User.objects.create_user(
            username="alice",
            email="alice@csss.com",
            password="Staff1234!",
            role="staff",
            module=self.module
        )

        # Student user (M2M modules)
        self.student = User.objects.create_user(
            username="bob",
            email="bob@csss.com",
            password="Stu1234!",
            role="student"
        )
        self.student.modules.add(self.module)

        # Another module + exam for cross-access tests
        other_module = Module.objects.create(code="MATH101", name="Mathematics")
        now = timezone.now()
        self.other_exam = Exam.objects.create(
            title="Other Exam",
            module=other_module,
            is_active=True,
            opens_at=now - timedelta(hours=1),
            closes_at=now + timedelta(hours=1),
        )

        # Exam in staff/student's shared module
        self.exam = Exam.objects.create(
            title="Permission Test Exam",
            module=self.module,
            is_active=True,
            opens_at=now - timedelta(hours=1),
            closes_at=now + timedelta(hours=1),
        )

    def test_student_cannot_access_staff_views(self):
        self.client.login(username="bob", password="Stu1234!")

        urls = [
            reverse("staff_results_overview"),
            reverse("staff_exam_results", args=[self.exam.id]),
            reverse("staff_exam_question_stats", args=[self.exam.id]),
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertIn(response.status_code, (302, 403), f"Student got access to {url}")

    def test_staff_cannot_access_student_views(self):
        self.client.login(username="alice", password="Staff1234!")

        urls = [
            reverse("exam_instructions", args=[self.exam.id]),
            reverse("take_exam_start", args=[self.exam.id]),
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertIn(response.status_code, (302, 403), f"Staff got access to {url}")

    def test_anonymous_redirects_to_login(self):
        urls = [
            reverse("staff_results_overview"),
            reverse("exam_instructions", args=[self.exam.id]),
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)
            # ✅ accept both default /accounts/login/ and custom /login/
            self.assertIn("/login", response.url, f"Anonymous redirect failed for {url}: got {response.url}")

    def test_staff_cannot_manage_exam_from_other_module(self):
        self.client.login(username="alice", password="Staff1234!")

        url = reverse("staff_exam_manage", args=[self.other_exam.id])
        response = self.client.get(url)
        # should redirect away (no access)
        self.assertIn(response.status_code, (302, 403))
