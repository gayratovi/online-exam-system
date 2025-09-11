from django.core.management.base import BaseCommand
from exams.models import Module


class Command(BaseCommand):
    help = "Seed 6 modules (creates or updates names)."

    def handle(self, *args, **options):
        modules = [
            ("MOD001", "Introduction to Computer Science"),
            ("MOD002", "Algorithms"),
            ("MOD003", "Data Structures"),
            ("MOD004", "Web Development"),
            ("MOD005", "Databases"),
            ("MOD006", "Operating Systems"),
        ]

        created_count = 0
        updated_count = 0

        for code, name in modules:
            module, created = Module.objects.get_or_create(
                code=code, defaults={"name": name}
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"✅ Created: {code} — {name}"))
            else:
                if module.name != name:
                    module.name = name
                    module.save(update_fields=["name"])
                    updated_count += 1
                    self.stdout.write(self.style.WARNING(f"✏️ Updated name for {code} → {name}"))
                else:
                    self.stdout.write(self.style.NOTICE(f"✔️ Already exists: {code} — {name}"))

        self.stdout.write(
            self.style.SUCCESS(
                f"Modules seeding complete. Created {created_count}, updated {updated_count}."
            )
        )