from django.urls import path
from django.contrib.auth import views as auth_views
from .views import register_view, login_view, logout_view, student_dashboard, staff_dashboard, role_based_redirect

urlpatterns = [
    path('', role_based_redirect, name='home'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('student/dashboard/', student_dashboard, name='student_dashboard'),
    path('staff/dashboard/', staff_dashboard, name='staff_dashboard'),

    # Password change
    path('password_change/', auth_views.PasswordChangeView.as_view(
        template_name='accounts/password_change.html'
    ), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='accounts/password_change_done.html'
    ), name='password_change_done'),
]