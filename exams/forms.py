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
        fields = ['title', 'description', 'is_active', 'opens_at', 'closes_at', 'duration_minutes', 'questions']
        widgets = {
            'opens_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'closes_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['questions'].queryset = Question.objects.filter(module=user.module)

    def clean(self):
        cleaned = super().clean()
        o, c = cleaned.get('opens_at'), cleaned.get('closes_at')
        if o and c and c <= o:
            raise forms.ValidationError('Closes at must be after Opens at.')
        return cleaned
