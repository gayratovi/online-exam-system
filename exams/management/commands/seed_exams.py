from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from exams.models import Module, Exam

class Command(BaseCommand):
    help = "Create 1–3 exams per module: first closed, second open, third upcoming."

    def handle(self, *args, **opts):
        now = timezone.now()
        titles_by_module = {
            # you can customize titles per module code if you want
            "MOD001": ["Final Knowledge Check", "Intro Weekly Quiz", "Intro Project Quiz"],
            "MOD002": ["Algorithms Midterm", "Greedy & DP Quiz", "Graphs Practice"],
            "MOD003": ["Data Structures Test", "Trees & Heaps Quiz", "Hashing Practice"],
            "MOD004": ["Web Dev Sprint Quiz", "HTTP & Forms Quiz", "JS Basics Practice"],
            "MOD005": ["Databases Practice", "SQL & Joins Quiz", "Indexes & Plans"],
            "MOD006": ["OS Concepts Quiz", "Processes & Threads Quiz", "Memory & Filesystems"],
        }

        for m in Module.objects.all().order_by('code'):
            titles = titles_by_module.get(m.code, [f"{m.code} — Exam A", f"{m.code} — Exam B", f"{m.code} — Exam C"])
            exams = []
            for i, title in enumerate(titles[:3], start=1):
                defaults = {
                    "description": f"{title} for {m.code}",
                    "duration_minutes": 60,
                }
                exam, _ = Exam.objects.get_or_create(module=m, title=title, defaults=defaults)
                exams.append(exam)

            # timings: 1 closed, 1 open, others upcoming
            if exams:
                e = exams[0]
                e.opens_at = now - timedelta(days=14)
                e.closes_at = now - timedelta(days=7)
                e.duration_minutes = e.duration_minutes or 60
                e.is_active = True
                e.save()
            if len(exams) >= 2:
                e = exams[1]
                e.opens_at = now - timedelta(days=1)
                e.closes_at = now + timedelta(days=7)
                e.duration_minutes = e.duration_minutes or 60
                e.is_active = True
                e.save()
            for e in exams[2:]:
                e.opens_at = now + timedelta(days=30)
                e.closes_at = now + timedelta(days=37)
                e.duration_minutes = e.duration_minutes or 60
                e.is_active = True
                e.save()

        self.stdout.write(self.style.SUCCESS("Exams seeded / normalized."))