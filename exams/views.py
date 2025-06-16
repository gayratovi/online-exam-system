from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import ExamCreationForm
from .models import Exam, ExamQuestion

@login_required
def create_exam_view(request):
    if request.user.role != 'admin':
        return redirect('login')

    if request.method == 'POST':
        form = ExamCreationForm(request.POST)
        if form.is_valid():
            exam = form.save()
            for question in form.cleaned_data['questions']:
                ExamQuestion.objects.create(exam=exam, question=question)
            return redirect('exam_list')  # to be created later
    else:
        form = ExamCreationForm()

    return render(request, 'exams/create_exam.html', {'form': form})
