from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

def home_redirect(request):
    return redirect('login')

urlpatterns = [
    path('admin/', admin.site.urls),

    # Accounts (login/register/logout)
    path('', include('accounts.urls')),

    # Staff-facing
    path('staff/', include('exams.urls_staff')),

    # Student-facing
    path('student/', include('exams.urls_student')),

    # Questions (if needed separately)
    path('questions/', include('questions.urls')),

    # Root → login
    path('', home_redirect),
]