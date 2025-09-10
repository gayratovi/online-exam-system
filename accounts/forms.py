from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
import re

User = get_user_model()

class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email", "role", "password1", "password2")

    def clean_username(self):
        username = self.cleaned_data.get("username")
        role = self.cleaned_data.get("role")

        if role == "student":
            # Must match CSSS ID format
            if not re.match(r"^CSSS25\d{3,}$", username):
                raise ValidationError("Student username must be a valid CSSS ID (e.g., CSSS251001).")
        elif role == "staff":
            # For staff we keep it simple: lowercase names only (alice, john, etc.)
            if not re.match(r"^[a-z]+$", username):
                raise ValidationError("Staff username must be lowercase letters only (e.g., alice).")
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        role = self.cleaned_data.get("role")
        username = self.cleaned_data.get("username")

        if not email:
            raise ValidationError("Email is required.")

        # Email must always be csss.com domain
        if not email.endswith("@csss.com"):
            raise ValidationError("Email must end with @csss.com.")

        if role == "student":
            # Students: email must match username
            if username and not email.startswith(username.lower()):
                raise ValidationError(f"Student email must match username: {username.lower()}@csss.com")
        elif role == "staff":
            # Staff: email must start with their username (alice@csss.com, john@csss.com, etc.)
            if username and not email.startswith(username):
                raise ValidationError(f"Staff email must match username: {username}@csss.com")
        return email