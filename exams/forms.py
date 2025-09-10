from django import forms
from django.utils import timezone
from .models import Exam
from questions.models import Question


class ExamCreationForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ["title", "description", "opens_at", "closes_at", "duration_minutes"]
        widgets = {
            "opens_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "closes_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        now = timezone.now()
        self.fields["opens_at"].initial = now
        self.fields["closes_at"].initial = now + timezone.timedelta(days=7)
        self.fields["duration_minutes"].initial = 60

    def clean(self):
        data = super().clean()
        opens = data.get("opens_at")
        closes = data.get("closes_at")
        if opens and closes and closes <= opens:
            raise forms.ValidationError("Closes At must be after Opens At.")
        return data


class NewQuestionForExamForm(forms.ModelForm):
    """
    Create a Question inline for an exam.
    Validation rules:
      - MCQ  -> options A–D required; correct_answer must be one of a/b/c/d
      - TF   -> correct_answer must be True/False
      - FILL -> correct_answer any non-empty string
    """
    class Meta:
        model = Question
        fields = [
            "question_text",
            "question_type",
            "option_a", "option_b", "option_c", "option_d",
            "correct_answer",
        ]
        widgets = {
            "question_text": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Default: text input
        self.fields["correct_answer"].widget = forms.TextInput()

        # Switch to dropdown if MCQ is selected
        data = kwargs.get("data")
        if data and data.get("question_type") == "MCQ":
            self.fields["correct_answer"].widget = forms.Select(choices=[
                ("a", "A"),
                ("b", "B"),
                ("c", "C"),
                ("d", "D"),
            ])

    def clean(self):
        cleaned = super().clean()
        qtype = cleaned.get("question_type")
        ca = (cleaned.get("correct_answer") or "").strip()

        if qtype == "MCQ":
            a = cleaned.get("option_a")
            b = cleaned.get("option_b")
            c = cleaned.get("option_c")
            d = cleaned.get("option_d")
            if not all([a, b, c, d]):
                raise forms.ValidationError("MCQ requires all four options A, B, C, and D.")
            if ca.lower() not in ("a", "b", "c", "d"):
                raise forms.ValidationError("For MCQ, correct answer must be one of: A, B, C, or D.")
            cleaned["correct_answer"] = ca.lower()

        elif qtype == "TF":
            if ca not in ("True", "False"):
                raise forms.ValidationError("For True/False, correct answer must be 'True' or 'False'.")

        elif qtype == "FILL":
            if not ca:
                raise forms.ValidationError("Fill-in-the-gap requires a non-empty correct answer.")

        else:
            raise forms.ValidationError("Unknown question type.")

        return cleaned
