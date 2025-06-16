from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import ExamCreationForm
from .models import Exam, ExamQuestion

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
