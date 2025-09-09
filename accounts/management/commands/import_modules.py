from django.core.management.base import BaseCommand, CommandError
import csv
from accounts.models import Module

class Command(BaseCommand):
    help = "Import modules from CSV: name,code"

    def add_arguments(self, parser):
        parser.add_argument('csv_path')

    def handle(self, *args, **opts):
        path = opts['csv_path']
        created, updated = 0, 0
        with open(path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            required = {'name', 'code'}
            if not required.issubset(reader.fieldnames or []):
                raise CommandError(f"CSV must have headers: {required}")
            for row in reader:
                name = (row['name'] or '').strip()
                code = (row['code'] or '').strip()
                if not name or not code:
                    self.stdout.write(self.style.WARNING(f"Skipping row: {row}"))
                    continue
                obj, was_created = Module.objects.update_or_create(
                    code=code, defaults={'name': name}
                )
                created += 1 if was_created else 0
                updated += 0 if was_created else 1
        self.stdout.write(self.style.SUCCESS(f"Modules imported. created={created}, updated={updated}"))
