import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

# Adjust this import if your Module model lives somewhere else
from exams.models import Module


class Command(BaseCommand):
    help = "Seed ~100 students with IDs and csss.com emails, enrolled into modules."

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=100, help="Number of students to create (default 100)")
        parser.add_argument("--prefix", type=str, default="BBK25", help="Student ID prefix (default BBK25)")
        parser.add_argument("--start", type=int, default=1001, help="Starting ID number (default 1001)")

    def handle(self, *args, **options):
        User = get_user_model()
        count = options["count"]
        prefix = options["prefix"]
        start = options["start"]

        # ensure modules exist
        modules_data = [
            ("MOD001", "Introduction to Computer Science"),
            ("MOD002", "Algorithms"),
            ("MOD003", "Data Structures"),
            ("MOD004", "Web Development"),
            ("MOD005", "Databases"),
            ("MOD006", "Operating Systems"),
        ]
        modules = []
        for code, name in modules_data:
            m, _ = Module.objects.get_or_create(code=code, defaults={"name": name})
            modules.append(m)

        created = 0
        for i in range(count):
            student_id = f"{prefix}{start+i}"  # e.g., BBK251001
            email = f"{student_id.lower()}@csss.com"

            user, was_created = User.objects.get_or_create(
                username=student_id,
                defaults={
                    "email": email,
                    "is_active": True,
                    "role": "student",  # adjust if your CustomUser uses a different field
                },
            )

            if was_created:
                # set password for new students
                user.set_password("Stu1234!")
                # if your model has a student_id field, save it
                if hasattr(user, "student_id"):
                    user.student_id = student_id
                user.save()
                created += 1

            # enroll in 1–3 random modules
            if hasattr(user, "modules"):  # M2M
                for m in random.sample(modules, k=random.choice([1, 2, 3])):
                    user.modules.add(m)
            elif hasattr(user, "module"):  # single FK
                m = random.choice(modules)
                user.module = m
                user.save()

        self.stdout.write(self.style.SUCCESS(
            f"Created {created} new students (total ensured: {count}). "
            f"Default password = Stu1234!"
        ))
