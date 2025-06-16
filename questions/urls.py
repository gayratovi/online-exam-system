from django.urls import path
from .views import add_question_view, question_list_view, edit_question_view, delete_question_view

urlpatterns = [
    path('add/', add_question_view, name='add_question'),
    path('list/', question_list_view, name='question_list'),
    path('edit/<int:question_id>/', edit_question_view, name='edit_question'),
    path('delete/<int:question_id>/', delete_question_view, name='delete_question'),
]
