from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from exams.models import Exam, Module

class Command(BaseCommand):
    help = "Per module: first exam closed, second open now, others upcoming next month."

    def handle(self, *args, **opts):
        now = timezone.now()
        for m in Module.objects.all():
            exams = list(Exam.objects.filter(module=m).order_by('id'))
            if not exams:
                continue

            # 1) closed last week
            e = exams[0]
            e.opens_at = now - timedelta(days=14)
            e.closes_at = now - timedelta(days=7)
            e.duration_minutes = e.duration_minutes or 60
            e.save()

            # 2) open now (if exists)
            if len(exams) >= 2:
                e = exams[1]
                e.opens_at = now - timedelta(days=1)
                e.closes_at = now + timedelta(days=7)
                e.duration_minutes = e.duration_minutes or 60
                e.save()

            # 3+) upcoming next month
            for e in exams[2:]:
                e.opens_at = now + timedelta(days=30)
                e.closes_at = now + timedelta(days=37)
                e.duration_minutes = e.duration_minutes or 60
                e.save()

        self.stdout.write(self.style.SUCCESS("Exam timings normalized."))
