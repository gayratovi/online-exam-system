from django.urls import path
from .views import add_question_view

urlpatterns = [
    path('add/', add_question_view, name='add_question'),
]
