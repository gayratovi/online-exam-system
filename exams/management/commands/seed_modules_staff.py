from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

# Adjust this import if your Module lives elsewhere
from exams.models import Module  # or from accounts.models import Module

class Command(BaseCommand):
    help = "Seed 6 modules and ensure 1 staff per module with @csss.com emails."

    def handle(self, *args, **options):
        User = get_user_model()

        modules = [
            ("MOD001", "Introduction to Computer Science"),
            ("MOD002", "Algorithms"),
            ("MOD003", "Data Structures"),
            ("MOD004", "Web Development"),
            ("MOD005", "Databases"),
            ("MOD006", "Operating Systems"),
        ]

        staff_for_module = {
            "MOD001": ("alice", "alice@csss.com"),
            "MOD002": ("john", "john@csss.com"),
            "MOD003": ("teacher2", "teacher2@csss.com"),
            "MOD004": ("teacher1", "teacher1@csss.com"),
            "MOD005": ("teacher5", "teacher5@csss.com"),
            "MOD006": ("teacher6", "teacher6@csss.com"),
        }

        for code, name in modules:
            module, _ = Module.objects.get_or_create(code=code, defaults={"name": name})
            if module.name != name:
                module.name = name
                module.save(update_fields=["name"])

            username, email = staff_for_module[code]
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": email,
                    "role": "staff",     # adjust if your CustomUser uses another field/value
                    "is_active": True,
                },
            )

            # ensure email domain is @csss.com even if user existed
            if user.email != email:
                user.email = email

            # attach module to staff (FK user.module). If you use M2M, change accordingly.
            if hasattr(user, "module_id"):
                if user.module_id != module.id:
                    user.module = module
            elif hasattr(user, "modules"):
                if not user.modules.filter(pk=module.pk).exists():
                    user.modules.add(module)
            else:
                self.stdout.write(self.style.WARNING(
                    f"Attach module manually for {username} (no module/modules field found)."
                ))

            if created:
                user.set_password("Pass1234!")  # change later
            user.save()

            self.stdout.write(self.style.SUCCESS(
                f"[OK] {code} → staff: {user.username} ({user.email})"
            ))

        self.stdout.write(self.style.SUCCESS("Done seeding staff with @csss.com emails."))
