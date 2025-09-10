from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import Module

class Command(BaseCommand):
    help = "Seed 6 staff (teachers), one per module, with fixed names and emails."

    def handle(self, *args, **options):
        User = get_user_model()

        teachers = [
            ("alice", "Alice Johnson", "alice@csss.com", "MOD001"),
            ("john", "John Smith", "john@csss.com", "MOD002"),
            ("david", "David Miller", "david@csss.com", "MOD003"),
            ("emma", "Emma Davis", "emma@csss.com", "MOD004"),
            ("sophia", "Sophia Brown", "sophia@csss.com", "MOD005"),
            ("michael", "Michael Wilson", "michael@csss.com", "MOD006"),
        ]

        created = 0
        for username, full_name, email, module_code in teachers:
            try:
                module = Module.objects.get(code=module_code)
            except Module.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Module {module_code} not found! Skipping {username}."))
                continue

            first_name, last_name = full_name.split(" ", 1)

            user, was_created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": email,
                    "first_name": first_name,
                    "last_name": last_name,
                    "role": "staff",
                    "is_active": True,
                },
            )

            if was_created:
                user.set_password("Teach1234!")  # default teacher password
                user.module = module
                user.save()
                created += 1
                self.stdout.write(self.style.SUCCESS(f"Created staff: {username} ({module_code})"))
            else:
                # Ensure role/module is updated if they already exist
                user.role = "staff"
                user.module = module
                user.save()

        self.stdout.write(self.style.SUCCESS(f"Staff seeding done. Created {created}, updated {len(teachers) - created}"))
