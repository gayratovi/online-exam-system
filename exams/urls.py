from django.urls import path
from . import views

urlpatterns = [
    # --- Staff exam creation ---
    path('create/', views.create_exam_view, name='create_exam'),

    # --- Student exam flow ---
    path('<int:exam_id>/start/', views.take_exam_start_view, name='take_exam_start'),
    path('<int:exam_id>/q/<int:question_index>/', views.take_exam_question_view, name='take_exam_question'),
    path('<int:exam_id>/submit/', views.submit_exam_view, name='submit_exam'),
    path('<int:exam_id>/result/', views.exam_result_view, name='exam_result'),

    # --- Staff analytics/results ---
    path('staff/overview/', views.staff_results_overview_view, name='staff_results_overview'),
    path('staff/exam/<int:exam_id>/', views.staff_exam_results_view, name='staff_exam_results'),
    path('staff/exam/<int:exam_id>/questions/', views.staff_exam_question_stats_view, name='staff_exam_question_stats'),
    path('staff/exam/<int:exam_id>/attempt/<int:attempt_id>/', views.staff_attempt_detail_view, name='staff_attempt_detail'),
    path('staff/exam/<int:exam_id>/export.csv', views.staff_exam_results_export_csv, name='staff_exam_results_export_csv'),
]
