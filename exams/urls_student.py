from django.urls import path
from . import views

urlpatterns = [
    path('exams/<int:exam_id>/instructions/', views.exam_instructions_view, name='exam_instructions'),
    path('exams/<int:exam_id>/start/', views.take_exam_start_view, name='take_exam_start'),
    path('exams/<int:exam_id>/q/<int:question_index>/', views.take_exam_question_view, name='take_exam_question'),
    path('exams/<int:exam_id>/submit/', views.submit_exam_view, name='submit_exam'),
    path('exams/<int:exam_id>/result/', views.exam_result_view, name='exam_result'),
]
