from django.urls import path
from .views import (
    create_exam_view,
    exam_list_view,
    student_exam_list_view,
    take_exam_view,
)

urlpatterns = [
    path('create/', create_exam_view, name='create_exam'),
    path('list/', exam_list_view, name='exam_list'),
    path('student/', student_exam_list_view, name='student_exam_list'),
    path('take/<int:exam_id>/', take_exam_view, name='take_exam'),
]