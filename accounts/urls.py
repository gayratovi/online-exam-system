from django.urls import path
from .views import register_view, login_view, logout_view, student_dashboard, admin_dashboard

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('student/dashboard/', student_dashboard, name='student_dashboard'),
    path('admin/dashboard/', admin_dashboard, name='admin_dashboard'),
]
