from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
import re
from django.contrib.auth.forms import AuthenticationForm

User = get_user_model()

class RegistrationForm(UserCreationForm):
    role = forms.ChoiceField(choices=User.ROLE_CHOICES)

    class Meta:
        model = User
        fields = ("username", "email", "role", "password1", "password2")

    def clean(self):
        cleaned = super().clean()
        username = cleaned.get("username")
        email = cleaned.get("email")
        role = cleaned.get("role")

        # --- Username rules ---
        if role == "student":
            if not re.match(r"^CSSS25\d{3,}$", username or ""):
                self.add_error("username", "Student username must be a valid CSSS ID (e.g., CSSS251001).")
        elif role == "staff":
            if not re.match(r"^[a-z]+$", username or ""):
                self.add_error("username", "Staff username must be lowercase letters only (e.g., alice).")

        # --- Email rules ---
        if not email:
            self.add_error("email", "Email is required.")
        elif not email.endswith("@csss.com"):
            self.add_error("email", "Email must end with @csss.com.")
        else:
            if role == "student":
                if username and not email.startswith(username.lower()):
                    self.add_error("email", f"Student email must match username: {username.lower()}@csss.com")
            elif role == "staff":
                if username and not email.startswith(username):
                    self.add_error("email", f"Staff email must match username: {username}@csss.com")

        return cleaned



class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(attrs={"autofocus": True})
    )
    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput,
    )

    class Meta:
        model = User
        fields = ("username", "password")
