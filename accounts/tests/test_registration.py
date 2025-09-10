from django.test import TestCase
from django.contrib.auth import get_user_model
from accounts.forms import RegistrationForm

User = get_user_model()

class RegistrationFormTests(TestCase):

    def test_valid_student_registration(self):
        form = RegistrationForm(data={
            "username": "CSSS251001",
            "email": "csss251001@csss.com",
            "role": "student",
            "password1": "Testpass123!",
            "password2": "Testpass123!",
        })
        self.assertTrue(form.is_valid(), form.errors)

    def test_invalid_student_username(self):
        form = RegistrationForm(data={
            "username": "STUDENT01",
            "email": "student01@csss.com",
            "role": "student",
            "password1": "Testpass123!",
            "password2": "Testpass123!",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)

    def test_student_email_mismatch(self):
        form = RegistrationForm(data={
            "username": "CSSS251002",
            "email": "wrong@csss.com",
            "role": "student",
            "password1": "Testpass123!",
            "password2": "Testpass123!",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_valid_staff_registration(self):
        form = RegistrationForm(data={
            "username": "alice",
            "email": "alice@csss.com",
            "role": "staff",
            "password1": "Teachpass123!",
            "password2": "Teachpass123!",
        })
        self.assertTrue(form.is_valid(), form.errors)

    def test_invalid_staff_email(self):
        form = RegistrationForm(data={
            "username": "alice",
            "email": "wrong@csss.com",
            "role": "staff",
            "password1": "Teachpass123!",
            "password2": "Teachpass123!",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)
