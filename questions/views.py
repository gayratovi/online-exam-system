from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from accounts.models import CustomUser
from .forms import QuestionForm

@login_required
def add_question_view(request):
    # Only allow access to users with admin role
    if request.user.role != 'admin':
        return redirect('login')  # or show a 403 Forbidden page

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('add_question')  # Redirect to same page after adding
    else:
        form = QuestionForm()

    return render(request, 'questions/add_question.html', {'form': form})
