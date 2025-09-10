import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from exams.models import Module


class Command(BaseCommand):
    help = "Seed 123 students with IDs, names, and csss.com emails, enrolled into modules."

    def handle(self, *args, **options):
        User = get_user_model()

        # --- ensure modules exist ---
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

        first_names = [
            "Alice", "John", "Maria", "David", "Sara", "Michael", "Emma", "Liam",
            "Olivia", "Noah", "Sophia", "James", "Isabella", "Ethan", "Mia",
            "Alexander", "Charlotte", "Benjamin", "Amelia", "Lucas", "Harper"
        ]
        last_names = [
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
            "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
            "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"
        ]

        # --- generate 123 students ---
        prefix = "CSSS25"
        count = 123
        start = 1001
        created = 0

        for i in range(count):
            student_id = f"{prefix}{start+i}"   # e.g., CSSS251001
            email = f"{student_id.lower()}@csss.com"

            first = random.choice(first_names)
            last = random.choice(last_names)

            user, was_created = User.objects.get_or_create(
                username=student_id,
                defaults={
                    "email": email,
                    "first_name": first,
                    "last_name": last,
                    "is_active": True,
                    "role": "student",
                },
            )

            if was_created:
                user.set_password("Stu1234!")
                user.save()
                created += 1

            # enroll in 1–3 random modules
            if hasattr(user, "modules"):  # M2M
                for m in random.sample(modules, k=random.choice([2, 3, 4])):
                    user.modules.add(m)
            elif hasattr(user, "module"):  # single FK
                m = random.choice(modules)
                user.module = m
                user.save()

        self.stdout.write(self.style.SUCCESS(
            f"Created {created} new students (total ensured: {count}). "
            f"Default password = Stu1234!"
        ))
