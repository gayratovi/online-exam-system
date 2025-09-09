from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import RegistrationForm, LoginForm

# Exams/attempts for dashboards
from exams.models import Exam, StudentExamAttempt


def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('staff_dashboard' if user.role == 'staff' else 'student_dashboard')
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('staff_dashboard' if user.role == 'staff' else 'student_dashboard')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def student_dashboard(request):
    # Only students should see this page
    if getattr(request.user, 'role', None) != 'student':
        return redirect('login')

    student = request.user
    modules = student.modules.all().order_by('code', 'name')

    # Active exams across student's modules
    exams_qs = (Exam.objects
                .filter(module__in=modules, is_active=True)
                .select_related('module')
                .order_by('module__code', 'title'))

    # Fetch attempts (both completed and not)
    attempts = (StudentExamAttempt.objects
                .filter(student=student, exam__in=exams_qs)
                .values('exam_id', 'id', 'completed'))
    attempt_map = {a['exam_id']: a for a in attempts}

    # Attach status + attempt_id to each exam
    exams = []
    for e in exams_qs:
        att = attempt_map.get(e.id)
        if att:
            if att['completed']:
                e.status = 'Completed'
                e.attempt_id = att['id']
            else:
                e.status = 'In Progress'
                e.attempt_id = att['id']
        else:
            e.status = 'Not Started'
            e.attempt_id = None
        exams.append(e)

    return render(request, 'accounts/student_dashboard.html', {
        'modules': modules,
        'exams': exams,
    })


@login_required
def staff_dashboard(request):
    # Only staff should see this page
    if getattr(request.user, 'role', None) != 'staff':
        return redirect('login')

    teacher = request.user
    exams = (Exam.objects
             .filter(module=teacher.module)
             .select_related('module')
             .order_by('-created_at'))

    return render(request, 'accounts/staff_dashboard.html', {
        'teacher': teacher,
        'module': teacher.module,
        'exams': exams,
    })


@login_required
def role_based_redirect(request):
    """Send authenticated users to the correct dashboard."""
    role = getattr(request.user, 'role', None)
    if role == 'staff':
        return redirect('staff_dashboard')
    if role == 'student':
        return redirect('student_dashboard')
    return redirect('login')
