from django.urls import path
from .views import register_view, login_view, logout_view, student_dashboard, staff_dashboard, role_based_redirect

urlpatterns = [
    path('', role_based_redirect, name='home'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('student/dashboard/', student_dashboard, name='student_dashboard'),
    path('staff/dashboard/', staff_dashboard, name='staff_dashboard'),
]
