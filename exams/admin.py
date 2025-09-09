from django.contrib import admin
from .models import Exam, ExamQuestion, StudentExamAttempt, StudentAnswer

class ExamQuestionInline(admin.TabularInline):  # or StackedInline
    model = ExamQuestion
    extra = 0
    show_change_link = True

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'is_active', 'created_at')
    list_filter = ('module', 'is_active')
    search_fields = ('title', 'description')
    inlines = [ExamQuestionInline]

@admin.register(ExamQuestion)
class ExamQuestionAdmin(admin.ModelAdmin):
    list_display = ('exam', 'question')
    list_filter = ('exam',)

@admin.register(StudentExamAttempt)
class StudentExamAttemptAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'started_at', 'completed', 'score')
    list_filter = ('exam', 'completed')

@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'question', 'selected_answer', 'is_correct')
    list_filter = ('is_correct',)
