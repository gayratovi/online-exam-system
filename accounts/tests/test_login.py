from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class LoginTests(TestCase):
    def setUp(self):
        # Create one student and one staff for login tests
        self.student = User.objects.create_user(
            username="CSSS251001",
            email="csss251001@csss.com",
            password="Stu1234!",
            role="student"
        )
        self.staff = User.objects.create_user(
            username="alice",
            email="alice@csss.com",
            password="Staff1234!",
            role="staff"
        )

    def test_student_login_redirects_to_dashboard(self):
        response = self.client.post(reverse("login"), {
            "username": "CSSS251001",
            "password": "Stu1234!",
        })
        self.assertRedirects(response, reverse("student_dashboard"))

    def test_staff_login_redirects_to_dashboard(self):
        response = self.client.post(reverse("login"), {
            "username": "alice",
            "password": "Staff1234!",
        })
        self.assertRedirects(response, reverse("staff_dashboard"))

    def test_invalid_login_stays_on_page(self):
        response = self.client.post(reverse("login"), {
            "username": "wronguser",
            "password": "wrongpass",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Login")  # still on login page
