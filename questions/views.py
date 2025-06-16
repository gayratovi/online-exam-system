from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import QuestionForm
from .models import Question
from django.shortcuts import get_object_or_404

@login_required
def edit_question_view(request, question_id):
    if request.user.role != 'admin':
        return redirect('login')

    question = get_object_or_404(Question, id=question_id)

    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            return redirect('question_list')
    else:
        form = QuestionForm(instance=question)

    return render(request, 'questions/edit_question.html', {'form': form, 'question': question})

@login_required
def question_list_view(request):
    if request.user.role != 'admin':
        return redirect('login')  # Or a 403 page later

    questions = Question.objects.all()
    return render(request, 'questions/question_list.html', {'questions': questions})

@login_required
def add_question_view(request):
    # Only allow access to users with admin role
    if request.user.role != 'admin':
        return redirect('login')  # or show a 403 Forbidden page

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.module = request.user.module
            form.save()
            return redirect('add_question')  # Redirect to same page after adding
    else:
        form = QuestionForm()

    return render(request, 'questions/add_question.html', {'form': form})

@login_required
def delete_question_view(request, question_id):
    if request.user.role != 'admin':
        return redirect('login')

    question = get_object_or_404(Question, id=question_id)

    if request.method == 'POST':
        question.delete()
        return redirect('question_list')

    return render(request, 'questions/confirm_delete.html', {'question': question})
