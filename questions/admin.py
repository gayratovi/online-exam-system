from django.contrib import admin
from .models import Question

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'question_type', 'correct_answer')
    list_filter = ('question_type',)
    search_fields = ('question_text',)
