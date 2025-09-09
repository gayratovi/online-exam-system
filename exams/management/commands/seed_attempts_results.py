import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model

from exams.models import Exam, ExamQuestion, StudentExamAttempt, StudentAnswer

class Command(BaseCommand):
    help = "Create graded attempts for closed exams; a few in-progress for open exams."

    def handle(self, *args, **opts):
        User = get_user_model()
        students = User.objects.filter(role="student") if hasattr(User, "role") else User.objects.all()

        def students_for_module(mod):
            if hasattr(User, "modules"):
                return students.filter(modules__id=mod.id).distinct()
            if hasattr(User, "module_id"):
                return students.filter(module_id=mod.id)
            return students

        now = timezone.now()
        closed_count = open_count = 0

        for exam in Exam.objects.all().select_related('module'):
            eqs = list(ExamQuestion.objects.filter(exam=exam).select_related('question'))
            if not eqs:
                continue

            pool = list(students_for_module(exam.module)[:60])
            random.shuffle(pool)

            # classify
            is_closed = bool(exam.closes_at and now >= exam.closes_at)
            is_open = (not exam.opens_at or exam.opens_at <= now) and (not exam.closes_at or now <= exam.closes_at)

            if is_closed:
                sample = pool[:20]
                for stu in sample:
                    attempt, _ = StudentExamAttempt.objects.get_or_create(
                        student=stu, exam=exam,
                        defaults={
                            "started_at": (exam.opens_at or now) + timedelta(hours=1),
                            "submitted_at": (exam.opens_at or now) + timedelta(hours=1, minutes=30),
                            "completed": True,
                        },
                    )
                    correct_count = 0
                    for link in eqs:
                        q = link.question
                        qtype = getattr(q, "question_type", "MCQ")
                        correct = getattr(q, "correct_answer", None)

                        if qtype == "MCQ":
                            pick = correct if random.random() < 0.7 else random.choice(["a", "b", "c", "d"])
                        elif qtype == "TF":
                            pick = "True" if random.random() < 0.7 else "False"
                            if correct not in ("True", "False"):
                                correct = "True"
                        elif qtype == "FILL":
                            pick = "seed" if random.random() < 0.6 else "wrong"
                        else:
                            # fallback (shouldn't really happen)
                            pick = "free"

                        is_corr = (correct is not None and pick == correct)
                        if is_corr:
                            correct_count += 1

                        StudentAnswer.objects.get_or_create(
                            attempt=attempt, question=q,
                            defaults={"selected_answer": pick, "is_correct": is_corr}
                        )

                    total_q = len(eqs)
                    pct = round((correct_count / total_q) * 100, 2) if total_q else 0
                    if attempt.score != pct or not attempt.completed or not attempt.submitted_at:
                        attempt.score = pct
                        attempt.completed = True
                        attempt.submitted_at = attempt.submitted_at or now
                        attempt.save()
                closed_count += 1

            elif is_open:
                # optional: a few in-progress
                for stu in pool[:8]:
                    StudentExamAttempt.objects.get_or_create(
                        student=stu, exam=exam,
                        defaults={"completed": False, "started_at": now}
                    )
                open_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Attempts seeded. Closed exams graded: {closed_count}, open exams in-progress updated: {open_count}"
        ))