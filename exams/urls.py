from django.urls import path
from .views import create_exam_view

urlpatterns = [
    path('create/', create_exam_view, name='create_exam'),
]