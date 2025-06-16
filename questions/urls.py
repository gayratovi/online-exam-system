from django.urls import path
from .views import add_question_view, question_list_view

urlpatterns = [
    path('add/', add_question_view, name='add_question'),
    path('list/', question_list_view, name='question_list'),
]
