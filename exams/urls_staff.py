from django.urls import path
from . import views

urlpatterns = [
    # Staff exam creation
    path('exams/create/', views.create_exam_view, name='create_exam'),

    # Staff analytics/results
    path('results/overview/', views.staff_results_overview_view, name='staff_results_overview'),
    path('exams/<int:exam_id>/', views.staff_exam_results_view, name='staff_exam_results'),
    path('exams/<int:exam_id>/questions/', views.staff_exam_question_stats_view, name='staff_exam_question_stats'),
    path('exams/<int:exam_id>/attempt/<int:attempt_id>/', views.staff_attempt_detail_view, name='staff_attempt_detail'),
    path('exams/<int:exam_id>/export.csv', views.staff_exam_results_export_csv, name='staff_exam_results_export_csv'),
]