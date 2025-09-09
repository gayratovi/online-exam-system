import random
from django.core.management.base import BaseCommand
from exams.models import Exam, ExamQuestion
from questions.models import Question

class Command(BaseCommand):
    help = "Attach 6–8 mixed questions (MCQ/TF/FILL) to each exam if none exist."

    def handle(self, *args, **opts):
        created_total = 0
        for exam in Exam.objects.all().select_related('module'):
            # skip if exam already has questions
            if ExamQuestion.objects.filter(exam=exam).exists():
                continue

            n = random.randint(6, 8)
            for i in range(1, n + 1):
                qtype = random.choice(["MCQ", "TF", "FILL"])
                q_defaults = {"question_type": qtype}

                q_kwargs = {
                    "module": exam.module,
                    "question_text": f"Q{i}. {exam.title}: {qtype} seeded question.",
                }

                # Fill fields per type
                if qtype == "MCQ":
                    q_defaults.update({
                        "option_a": f"{exam.title} — Option A",
                        "option_b": f"{exam.title} — Option B",
                        "option_c": f"{exam.title} — Option C",
                        "option_d": f"{exam.title} — Option D",
                        "correct_answer": random.choice(["a", "b", "c", "d"]),
                    })
                elif qtype == "TF":
                    q_defaults["correct_answer"] = random.choice(["True", "False"])
                else:  # FILL
                    q_defaults["correct_answer"] = "seed"  # a short expected string

                q, _ = Question.objects.get_or_create(
                    **q_kwargs, defaults=q_defaults
                )
                ExamQuestion.objects.get_or_create(exam=exam, question=q)
                created_total += 1

            self.stdout.write(self.style.SUCCESS(f"[OK] {exam.title}: added {n} questions"))

        self.stdout.write(
            self.style.SUCCESS(f"Questions seeding done. Total created links: {created_total}")
        )