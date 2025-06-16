from django import forms
from .models import Exam
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

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')  # Expect the current user to be passed in
        super().__init__(*args, **kwargs)
        self.fields['questions'].queryset = Question.objects.filter(module=user.module)