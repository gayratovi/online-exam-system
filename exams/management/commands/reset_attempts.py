from django.core.management.base import BaseCommand
from exams.models import StudentExamAttempt, StudentAnswer

class Command(BaseCommand):
    help = "Clear all student attempts and answers (for reseeding)."

    def handle(self, *args, **options):
        StudentAnswer.objects.all().delete()
        StudentExamAttempt.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("✅ Cleared all student attempts and answers"))