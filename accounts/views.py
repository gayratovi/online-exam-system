from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm, LoginForm

def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)

            # Redirect based on role
            if user.role == 'admin':
                return redirect('add_question')
            elif user.role == 'student':
                return redirect('student_dashboard')
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # Redirect based on role
            if user.role == 'admin':
                return redirect('add_question')
            elif user.role == 'student':
                return redirect('student_dashboard')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def student_dashboard(request):
    return render(request, 'accounts/student_dashboard.html')


@login_required
def admin_dashboard(request):
    return render(request, 'accounts/admin_dashboard.html')
