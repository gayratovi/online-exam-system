from datetime import timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .forms import ExamCreationForm
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
        form = ExamCreationForm(request.POST, user=request.user)
        if form.is_valid():
            exam = form.save(commit=False)
            exam.module = request.user.module
            exam.save()
            for question in form.cleaned_data['questions']:
                ExamQuestion.objects.create(exam=exam, question=question)
            return redirect('staff_dashboard')
    else:
        form = ExamCreationForm(user=request.user)

    return render(request, 'exams/create_exam.html', {'form': form})

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
        attempt.save()

    # if time already over, submit immediately
    if attempt.is_time_over():
        return redirect('submit_exam', exam_id=exam.id)

    # jump to first unanswered
    questions = list(Question.objects.filter(examquestion__exam=exam).order_by('id'))
    if not questions:
        return redirect('student_dashboard')

    answered_ids = set(
        StudentAnswer.objects.filter(attempt=attempt).values_list('question_id', flat=True)
    )
    first_index = 0
    for i, q in enumerate(questions):
        if q.id not in answered_ids:
            first_index = i
            break

    return redirect('take_exam_question', exam_id=exam.id, question_index=first_index)


@login_required
def take_exam_question_view(request, exam_id, question_index: int):
    if request.user.role != 'student':
        return redirect('login')

    exam = get_object_or_404(Exam, id=exam_id, is_active=True)
    if not request.user.modules.filter(pk=exam.module_id).exists():
        return redirect('student_dashboard')

    attempt = StudentExamAttempt.objects.filter(
        student=request.user, exam=exam, completed=False
    ).first()
    if not attempt:
        # no ongoing attempt → start flow
        return redirect('take_exam_start', exam_id=exam.id)

    # hard gates: exam window & time budget
    if not exam.is_open_now() or attempt.is_time_over():
        return redirect('submit_exam', exam_id=exam.id)

    questions = list(Question.objects.filter(examquestion__exam=exam).order_by('id'))
    total = len(questions)
    if total == 0:
        return redirect('student_dashboard')
    if question_index < 0 or question_index >= total:
        return redirect('take_exam_question', exam_id=exam.id, question_index=0)

    question = questions[question_index]

    prev = StudentAnswer.objects.filter(attempt=attempt, question=question).first()
    prefill = prev.selected_answer if prev else ""

    if request.method == 'POST':
        # If time ran out between render and POST, submit
        if attempt.is_time_over():
            return redirect('submit_exam', exam_id=exam.id)

        selected_answer = (request.POST.get('answer') or "").strip()

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

    answers = (StudentAnswer.objects
               .filter(attempt=attempt)
               .select_related('question')
               .order_by('question__id'))

    total = ExamQuestion.objects.filter(exam=exam).count()
    correct = answers.filter(is_correct=True).count()

    return render(request, 'exams/exam_result.html', {
        'exam': exam,
        'attempt': attempt,
        'answers': answers,
        'total': total,
        'correct': correct,
        'score': attempt.score,
    })