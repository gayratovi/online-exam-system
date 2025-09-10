from datetime import timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .forms import ExamCreationForm, NewQuestionForExamForm
from .models import Exam, ExamQuestion, StudentExamAttempt, StudentAnswer
from questions.models import Question
from django.db.models import Count, Avg, Q, F, ExpressionWrapper, DurationField
from django.http import HttpResponse


# ---------- STAFF VIEWS ----------
@login_required
def create_exam_view(request):
    if request.user.role != 'staff':
        return redirect('login')

    if request.method == 'POST':
        form = ExamCreationForm(request.POST)
        if form.is_valid():
            exam = form.save(commit=False)
            exam.module = request.user.module  # lock to teacher's module
            exam.is_active = True
            exam.save()
            messages.success(request, "Exam created. Now add questions.")
            return redirect('staff_exam_questions_manage', exam_id=exam.id)
    else:
        form = ExamCreationForm()

    return render(request, 'exams/create_exam.html', {'form': form})


@login_required
def staff_exam_manage_view(request, exam_id):
    """Page to edit exam details and access question management."""
    if request.user.role != 'staff':
        return redirect('login')

    exam = get_object_or_404(Exam, pk=exam_id)
    if exam.module != request.user.module:
        messages.error(request, "You can only manage exams in your module.")
        return redirect('staff_dashboard')

    if request.method == "POST":
        form = ExamCreationForm(request.POST, instance=exam)
        if form.is_valid():
            form.save()
            messages.success(request, "Exam details updated.")
            return redirect('staff_exam_manage', exam_id=exam.id)
    else:
        form = ExamCreationForm(instance=exam)

    return render(request, 'exams/manage_exam.html', {
        'exam': exam,
        'form': form,
    })


@login_required
def staff_exam_questions_manage_view(request, exam_id):
    """Separate page to manage questions of an exam."""
    if request.user.role != 'staff':
        return redirect('login')

    exam = get_object_or_404(Exam, pk=exam_id)
    if exam.module != request.user.module:
        messages.error(request, "You can only manage exams in your module.")
        return redirect('staff_dashboard')

    # --- Add Question Form ---
    if request.method == "POST":
        q_form = NewQuestionForExamForm(request.POST)
        if q_form.is_valid():
            q = q_form.save(commit=False)

            # Ensure module is always set (required field)
            q.module = exam.module
            q.save()

            # Always link to exam
            eq, created = ExamQuestion.objects.get_or_create(exam=exam, question=q)

            if created:
                messages.success(request, f"Question added: {q.question_text[:50]}...")
            else:
                messages.info(request, "This question was already linked to the exam.")

            return redirect('staff_exam_questions_manage', exam_id=exam.id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        q_form = NewQuestionForExamForm()

    # Existing questions linked to this exam
    linked = (ExamQuestion.objects
              .filter(exam=exam)
              .select_related('question')
              .order_by('question__id'))

    return render(request, 'exams/manage_exam_questions.html', {
        'exam': exam,
        'q_form': q_form,
        'linked': linked,
    })


@login_required
def staff_exam_question_delete_view(request, exam_id, question_id):
    """Remove a question from an exam (does not delete the Question object globally)."""
    if request.user.role != 'staff':
        return redirect('login')

    exam = get_object_or_404(Exam, pk=exam_id)
    if exam.module != request.user.module:
        messages.error(request, "You can only manage exams in your module.")
        return redirect('staff_dashboard')

    eq = get_object_or_404(ExamQuestion, exam=exam, question_id=question_id)
    eq.delete()
    messages.success(request, "Question removed from the exam.")
    return redirect('staff_exam_questions_manage', exam_id=exam.id)


@login_required
def staff_exam_delete_view(request, exam_id):
    """Delete an exam completely (only from teacher’s module)."""
    if request.user.role != 'staff':
        return redirect('login')

    exam = get_object_or_404(Exam, pk=exam_id)
    if exam.module != request.user.module:
        messages.error(request, "You can only delete exams in your own module.")
        return redirect('staff_dashboard')

    if request.method == "POST":
        exam.delete()
        messages.success(request, "Exam deleted successfully.")
        return redirect('staff_dashboard')

    return redirect('staff_exam_manage', exam_id=exam.id)

# ---------- STAFF ANALYTICS ----------

@login_required
def staff_results_overview_view(request):
    if request.user.role != 'staff':
        return redirect('login')

    exams = (Exam.objects
             .filter(module=request.user.module)
             .annotate(
                 attempts_total=Count('studentexamattempt', distinct=True),
                 attempts_completed=Count('studentexamattempt', filter=Q(studentexamattempt__completed=True), distinct=True),
                 avg_score=Avg('studentexamattempt__score'),
             )
             .order_by('-created_at'))

    # Pre-compute completion % safely (no template math needed)
    overview = []
    for e in exams:
        total = e.attempts_total or 0
        completed = e.attempts_completed or 0
        completion_pct = round((completed / total) * 100, 1) if total else None
        overview.append({
            'id': e.id,
            'title': e.title,
            'opens_at': e.opens_at,
            'closes_at': e.closes_at,
            'duration_minutes': e.duration_minutes,
            'attempts_total': total,
            'attempts_completed': completed,
            'completion_pct': completion_pct,
            'avg_score': round(e.avg_score, 2) if e.avg_score is not None else None,
        })

    return render(request, 'exams/staff_overview.html', {'overview': overview})


@login_required
def staff_exam_results_view(request, exam_id):
    if request.user.role != 'staff':
        return redirect('login')

    exam = get_object_or_404(Exam, pk=exam_id)
    if exam.module != request.user.module:
        return redirect('staff_dashboard')

    # duration: submitted_at - started_at
    time_taken = ExpressionWrapper(F('submitted_at') - F('started_at'), output_field=DurationField())
    attempts = (StudentExamAttempt.objects
                .filter(exam=exam)
                .select_related('student')
                .annotate(time_taken=time_taken)
                .order_by('-submitted_at', '-started_at'))

    total = attempts.count()
    completed_qs = attempts.filter(completed=True)
    completed = completed_qs.count()
    avg_score = completed_qs.aggregate(Avg('score'))['score__avg']
    avg_score = round(avg_score, 2) if avg_score is not None else None

    # shape rows for simple template rendering
    rows = []
    for a in attempts:
        # time_taken may be None if in progress
        tt = None
        if a.time_taken:
            total_sec = int(a.time_taken.total_seconds())
            h, rem = divmod(total_sec, 3600)
            m, s = divmod(rem, 60)
            tt = f'{h:02d}:{m:02d}:{s:02d}'
        rows.append({
            'id': a.id,
            'username': a.student.username,
            'score': float(a.score) if a.completed and a.score is not None else None,
            'started_at': a.started_at,
            'submitted_at': a.submitted_at,
            'time_taken': tt,
            'status': 'Completed' if a.completed else 'In Progress',
        })

    return render(request, 'exams/staff_exam_results.html', {
        'exam': exam,
        'total': total,
        'completed': completed,
        'avg_score': avg_score,
        'attempts': rows,
    })


@login_required
def staff_exam_question_stats_view(request, exam_id):
    if request.user.role != 'staff':
        return redirect('login')

    exam = get_object_or_404(Exam, pk=exam_id)
    if exam.module != request.user.module:
        return redirect('staff_dashboard')

    qstats = (ExamQuestion.objects
              .filter(exam=exam)
              .select_related('question')
              .annotate(
                  attempts_count=Count('question__studentanswer', filter=Q(question__studentanswer__attempt__exam=exam), distinct=True),
                  correct_count=Count('question__studentanswer', filter=Q(question__studentanswer__attempt__exam=exam,
                                                                         question__studentanswer__is_correct=True), distinct=True),
              )
              .order_by('question__id'))

    rows = []
    for idx, row in enumerate(qstats, start=1):
        attempts_count = row.attempts_count or 0
        correct_count = row.correct_count or 0
        pct = round((correct_count / attempts_count) * 100, 1) if attempts_count else None
        rows.append({
            'n': idx,
            'text': row.question.question_text,
            'attempts': attempts_count,
            'correct': correct_count,
            'pct': pct,
        })

    return render(request, 'exams/staff_exam_question_stats.html', {
        'exam': exam,
        'qrows': rows,
    })


@login_required
def staff_attempt_detail_view(request, exam_id, attempt_id):
    if request.user.role != 'staff':
        return redirect('login')

    exam = get_object_or_404(Exam, pk=exam_id)
    if exam.module != request.user.module:
        return redirect('staff_dashboard')

    attempt = get_object_or_404(StudentExamAttempt.objects.select_related('student'), pk=attempt_id, exam=exam)
    answers = (StudentAnswer.objects
               .filter(attempt=attempt)
               .select_related('question')
               .order_by('question__id'))

    # simple time taken
    time_str = '-'
    if attempt.submitted_at and attempt.started_at:
        total_sec = int((attempt.submitted_at - attempt.started_at).total_seconds())
        h, rem = divmod(total_sec, 3600)
        m, s = divmod(rem, 60)
        time_str = f'{h:02d}:{m:02d}:{s:02d}'

    return render(request, 'exams/staff_attempt_detail.html', {
        'exam': exam,
        'attempt': attempt,
        'answers': answers,
        'time_taken': time_str,
    })


@login_required
def staff_exam_results_export_csv(request, exam_id):
    if request.user.role != 'staff':
        return redirect('login')

    exam = get_object_or_404(Exam, pk=exam_id)
    if exam.module != request.user.module:
        return redirect('staff_dashboard')

    attempts = (StudentExamAttempt.objects
                .filter(exam=exam, completed=True)
                .select_related('student')
                .order_by('student__username'))

    resp = HttpResponse(content_type='text/csv')
    resp['Content-Disposition'] = f'attachment; filename="exam_{exam.id}_results.csv"'
    resp.write('username,full_name,score,started_at,submitted_at,time_taken_secs\n')

    for a in attempts:
        full_name = f"{a.student.first_name} {a.student.last_name}".strip().replace(',', ' ')
        secs = ''
        if a.submitted_at and a.started_at:
            secs = int((a.submitted_at - a.started_at).total_seconds())
        score = a.score if a.score is not None else ''
        resp.write(f"{a.student.username},{full_name},{score},{a.started_at},{a.submitted_at or ''},{secs}\n")

    return resp


# ---------- STUDENT VIEWS ----------

import random

@login_required
def take_exam_start_view(request, exam_id):
    if request.user.role != 'student':
        return redirect('login')

    exam = get_object_or_404(Exam, id=exam_id, is_active=True)

    if not request.user.modules.filter(pk=exam.module_id).exists():
        return redirect('student_dashboard')

    # exam must be open in its window
    if not exam.is_open_now():
        messages.error(request, "This exam is not currently open.")
        return redirect('student_dashboard')

    # if already completed, go to result
    existing_completed = StudentExamAttempt.objects.filter(
        student=request.user, exam=exam, completed=True
    ).first()
    if existing_completed:
        return redirect('exam_result', exam_id=exam.id)

    # get or create ongoing attempt
    attempt, created = StudentExamAttempt.objects.get_or_create(
        student=request.user, exam=exam, completed=False
    )
    if created or not attempt.ends_at:
        attempt.started_at = timezone.now()
        attempt.ends_at = attempt.started_at + timedelta(minutes=exam.duration_minutes)

        # assign random question order once per attempt
        q_ids = list(Question.objects.filter(examquestion__exam=exam).values_list("id", flat=True))
        random.shuffle(q_ids)
        attempt.question_order = q_ids

        attempt.save()

    # if time already over, submit immediately
    if attempt.is_time_over():
        return redirect('submit_exam', exam_id=exam.id)

    # jump to first unanswered
    questions = attempt.question_order or []
    if not questions:
        return redirect('student_dashboard')

    answered_ids = set(
        StudentAnswer.objects.filter(attempt=attempt).values_list('question_id', flat=True)
    )
    first_index = 0
    for i, qid in enumerate(questions):
        if qid not in answered_ids:
            first_index = i
            break

    return redirect('take_exam_question', exam_id=exam.id, question_index=first_index)

@login_required
def exam_instructions_view(request, exam_id):
    if request.user.role != "student":
        return redirect("login")

    exam = get_object_or_404(Exam, pk=exam_id)

    # only allow if exam is open
    if not exam.is_open_now():
        messages.error(request, "This exam is not currently open.")
        return redirect("student_dashboard")

    return render(request, "exams/exam_instructions.html", {
        "exam": exam,
    })

@login_required
def take_exam_question_view(request, exam_id, question_index: int):
    if request.user.role != 'student':
        return redirect('login')

    exam = get_object_or_404(Exam, id=exam_id, is_active=True)
    if not request.user.modules.filter(pk=exam.module_id).exists():
        return redirect('student_dashboard')

    # get ongoing attempt
    attempt = StudentExamAttempt.objects.filter(
        student=request.user, exam=exam, completed=False
    ).first()
    if not attempt:
        return redirect('take_exam_start', exam_id=exam.id)

    # hard gates: exam window & time budget
    if not exam.is_open_now() or attempt.is_time_over():
        return redirect('submit_exam', exam_id=exam.id)

    # use stored random question order
    question_ids = attempt.question_order or []
    total = len(question_ids)
    if total == 0:
        return redirect('student_dashboard')
    if question_index < 0 or question_index >= total:
        return redirect('take_exam_question', exam_id=exam.id, question_index=0)

    # fetch current question in that order
    question_id = question_ids[question_index]
    question = get_object_or_404(Question, id=question_id)

    # check if already answered
    prev = StudentAnswer.objects.filter(attempt=attempt, question=question).first()
    prefill = prev.selected_answer if prev else ""

    if request.method == 'POST':
        if attempt.is_time_over():
            return redirect('submit_exam', exam_id=exam.id)

        selected_answer = (request.POST.get('answer') or "").strip()

        # save/update answer
        StudentAnswer.objects.update_or_create(
            attempt=attempt,
            question=question,
            defaults={
                'selected_answer': selected_answer,
                'is_correct': selected_answer.lower() == question.correct_answer.lower()
            }
        )

        if 'prev' in request.POST:
            return redirect('take_exam_question', exam_id=exam.id, question_index=question_index - 1)
        if 'next' in request.POST:
            return redirect('take_exam_question', exam_id=exam.id, question_index=question_index + 1)
        if 'submit' in request.POST:
            return redirect('submit_exam', exam_id=exam.id)

    remaining = attempt.remaining_seconds()

    return render(request, 'exams/take_question.html', {
        'exam': exam,
        'question': question,
        'question_index': question_index,
        'total_questions': total,
        'prefill': prefill,
        'has_prev': question_index > 0,
        'has_next': question_index < total - 1,
        'remaining_seconds': remaining or 0,
    })


@login_required
def submit_exam_view(request, exam_id):
    if request.user.role != 'student':
        return redirect('login')

    exam = get_object_or_404(Exam, id=exam_id, is_active=True)
    attempt = StudentExamAttempt.objects.filter(
        student=request.user, exam=exam, completed=False
    ).first()
    if not attempt:
        # Already submitted or never started
        completed = StudentExamAttempt.objects.filter(student=request.user, exam=exam, completed=True).first()
        if completed:
            return redirect('exam_result', exam_id=exam.id)
        return redirect('student_dashboard')

    # finalize scoring
    answers = StudentAnswer.objects.filter(attempt=attempt)
    total_q = ExamQuestion.objects.filter(exam=exam).count()
    correct = answers.filter(is_correct=True).count()
    score = round((correct / total_q) * 100, 2) if total_q else 0

    attempt.score = score
    attempt.completed = True
    attempt.submitted_at = timezone.now()
    attempt.save()

    return redirect('exam_result', exam_id=exam.id)

@login_required
def exam_result_view(request, exam_id):
    if request.user.role != 'student':
        return redirect('login')

    exam = get_object_or_404(Exam, id=exam_id, is_active=True)

    # Get the completed attempt for this student+exam
    attempt = get_object_or_404(
        StudentExamAttempt,
        student=request.user,
        exam=exam,
        completed=True
    )

    # Fetch all answers
    answers_qs = (StudentAnswer.objects
                  .filter(attempt=attempt)
                  .select_related('question'))

    # If question order was stored, use it; otherwise fallback to ID order
    if attempt.question_order:
        answers_map = {a.question.id: a for a in answers_qs}
        answers = [answers_map[qid] for qid in attempt.question_order if qid in answers_map]
    else:
        answers = list(answers_qs.order_by('question__id'))

    total = ExamQuestion.objects.filter(exam=exam).count()
    correct = sum(1 for a in answers if a.is_correct)

    return render(request, 'exams/exam_result.html', {
        'exam': exam,
        'attempt': attempt,
        'answers': answers,
        'total': total,
        'correct': correct,
        'score': attempt.score,
    })