from django import forms
from .models import Question

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = [
            'question_text',
            'question_type',
            'option_a',
            'option_b',
            'option_c',
            'option_d',
            'correct_answer'
        ]
