from django import forms
from .models import Exam, ExamQuestion
from questions.models import Question

class ExamCreationForm(forms.ModelForm):
    questions = forms.ModelMultipleChoiceField(
        queryset=Question.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    class Meta:
        model = Exam
        fields = ['title', 'description', 'is_active', 'questions']
