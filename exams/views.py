from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import ExamCreationForm
from .models import Exam, ExamQuestion, StudentExamAttempt

@login_required
def create_exam_view(request):
    if request.user.role != 'admin':
        return redirect('login')

    if request.method == 'POST':
        form = ExamCreationForm(request.POST, user=request.user)  # ✅ pass user
        if form.is_valid():
            exam = form.save(commit=False)
            exam.module = request.user.module  # ✅ auto-assign module
            exam.save()
            for question in form.cleaned_data['questions']:
                ExamQuestion.objects.create(exam=exam, question=question)
            return redirect('exam_list')  # (you’ll build this next)
    else:
        form = ExamCreationForm(user=request.user)  # ✅ pass user to form

    return render(request, 'exams/create_exam.html', {'form': form})

@login_required
def exam_list_view(request):from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import ExamCreationForm
from .models import Exam, ExamQuestion, StudentExamAttempt

@login_required
def create_exam_view(request):
    if request.user.role != 'admin':
        return redirect('login')

    if request.method == 'POST':
        form = ExamCreationForm(request.POST, user=request.user)  # ✅ pass user
        if form.is_valid():
            exam = form.save(commit=False)
            exam.module = request.user.module  # ✅ auto-assign module
            exam.save()
            for question in form.cleaned_data['questions']:
                ExamQuestion.objects.create(exam=exam, question=question)
            return redirect('exam_list')  # (you’ll build this next)
    else:
        form = ExamCreationForm(user=request.user)  # ✅ pass user to form

    return render(request, 'exams/create_exam.html', {'form': form})

@login_required
def exam_list_view(request):
    if request.user.role != 'admin':
        return redirect('login')

    exams = Exam.objects.filter(module=request.user.module)
    return render(request, 'exams/exam_list.html', {'exams': exams})

@login_required
def student_exam_list_view(request):
    if request.user.role != 'student':
        return redirect('login')

    # Show only active exams for the student's module
    exams = Exam.objects.filter(module=request.user.module, is_active=True)

    # Optional: filter out exams they've already completed
    attempted_exam_ids = StudentExamAttempt.objects.filter(student=request.user).values_list('exam_id', flat=True)
    exams = exams.exclude(id__in=attempted_exam_ids)

    return render(request, 'exams/student_exam_list.html', {'exams': exams})
    if request.user.role != 'admin':
        return redirect('login')

    exams = Exam.objects.filter(module=request.user.module)
    return render(request, 'exams/exam_list.html', {'exams': exams})

@login_required
def student_exam_list_view(request):
    if request.user.role != 'student':
        return redirect('login')

    # Show only active exams for the student's module
    exams = Exam.objects.filter(module=request.user.module, is_active=True)

    # Optional: filter out exams they've already completed
    attempted_exam_ids = StudentExamAttempt.objects.filter(student=request.user).values_list('exam_id', flat=True)
    exams = exams.exclude(id__in=attempted_exam_ids)

    return render(request, 'exams/student_exam_list.html', {'exams': exams})