from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ExamCreationForm
from .models import Exam, ExamQuestion, StudentExamAttempt, StudentAnswer
from questions.models import Question


# ---------- STAFF VIEWS ----------
@login_required
def create_exam_view(request):
    if request.user.role != 'staff':
        return redirect('login')

    if request.method == 'POST':
        form = ExamCreationForm(request.POST, user=request.user)
        if form.is_valid():
            exam = form.save(commit=False)
            exam.module = request.user.module
            exam.save()
            for question in form.cleaned_data['questions']:
                ExamQuestion.objects.create(exam=exam, question=question)
            return redirect('exam_list')
    else:
        form = ExamCreationForm(user=request.user)

    return render(request, 'exams/create_exam.html', {'form': form})


@login_required
def exam_list_view(request):
    if request.user.role != 'staff':
        return redirect('login')

    exams = Exam.objects.filter(module=request.user.module)
    return render(request, 'exams/exam_list.html', {'exams': exams})


# ---------- STUDENT VIEWS ----------
@login_required
def student_exam_list_view(request):
    if request.user.role != 'student':
        return redirect('login')

    exams = Exam.objects.filter(module=request.user.module, is_active=True)

    attempted_exam_ids = StudentExamAttempt.objects.filter(
        student=request.user
    ).values_list('exam_id', flat=True)

    exams = exams.exclude(id__in=attempted_exam_ids)

    return render(request, 'exams/student_exam_list.html', {'exams': exams})


@login_required
def take_exam_view(request, exam_id):
    if request.user.role != 'student':
        return redirect('login')

    exam = get_object_or_404(Exam, id=exam_id)

    if exam.module != request.user.module:
        return redirect('student_exam_list')

    questions = Question.objects.filter(examquestion__exam=exam)

    if request.method == 'POST':
        # Step 1: Create exam attempt
        attempt = StudentExamAttempt.objects.create(
            student=request.user,
            exam=exam,
            completed=True  # marked complete at submission
        )

        correct_count = 0  # to calculate score

        # Step 2: Save each answer
        for question in questions:
            user_answer = request.POST.get(str(question.id), "").strip()
            is_correct = user_answer.lower() == question.correct_answer.strip().lower()

            StudentAnswer.objects.create(
                attempt=attempt,
                question=question,
                selected_answer=user_answer,
                is_correct=is_correct
            )

            if is_correct:
                correct_count += 1

        # Step 3: Calculate and save score
        total_questions = questions.count()
        score = (correct_count / total_questions) * 100
        attempt.score = round(score, 2)
        attempt.save()

        return redirect('student_dashboard')

    return render(request, 'exams/take_exam.html', {'exam': exam, 'questions': questions})
