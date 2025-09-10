from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from exams.models import Module, Exam

class Command(BaseCommand):
    help = "Reset and create exactly 3 exams per module: one closed, one open, one upcoming."

    def handle(self, *args, **opts):
        now = timezone.now()
        titles_by_module = {
            "MOD001": ["Final Knowledge Check", "Intro Weekly Quiz", "Intro Project Quiz"],
            "MOD002": ["Algorithms Midterm", "Greedy & DP Quiz", "Graphs Practice"],
            "MOD003": ["Data Structures Test", "Trees & Heaps Quiz", "Hashing Practice"],
            "MOD004": ["Web Dev Sprint Quiz", "HTTP & Forms Quiz", "JS Basics Practice"],
            "MOD005": ["Databases Practice", "SQL & Joins Quiz", "Indexes & Plans"],
            "MOD006": ["OS Concepts Quiz", "Processes & Threads Quiz", "Memory & Filesystems"],
        }

        for m in Module.objects.all().order_by("code"):
            # Delete old exams for this module
            Exam.objects.filter(module=m).delete()

            titles = titles_by_module.get(
                m.code,
                [f"{m.code} — Exam A", f"{m.code} — Exam B", f"{m.code} — Exam C"],
            )

            # 1. Closed exam
            Exam.objects.create(
                module=m,
                title=titles[0],
                description=f"{titles[0]} for {m.code}",
                duration_minutes=60,
                opens_at=now - timedelta(days=30),
                closes_at=now - timedelta(days=20),
                is_active=True,
            )

            # 2. Open exam
            Exam.objects.create(
                module=m,
                title=titles[1],
                description=f"{titles[1]} for {m.code}",
                duration_minutes=60,
                opens_at=now - timedelta(days=3),
                closes_at=now + timedelta(days=5),
                is_active=True,
            )

            # 3. Upcoming exam
            Exam.objects.create(
                module=m,
                title=titles[2],
                description=f"{titles[2]} for {m.code}",
                duration_minutes=60,
                opens_at=now + timedelta(days=15),
                closes_at=now + timedelta(days=25),
                is_active=True,
            )

        self.stdout.write(self.style.SUCCESS("✅ Exams reset: 1 closed, 1 open, 1 upcoming per module."))