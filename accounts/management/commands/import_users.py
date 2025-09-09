from django.core.management.base import BaseCommand, CommandError
import csv
from django.contrib.auth import get_user_model
from accounts.models import Module

User = get_user_model()

class Command(BaseCommand):
    help = "Import users from CSV. Headers: username,email,first_name,last_name,role,module_code,modules,password"

    def add_arguments(self, parser):
        parser.add_argument('csv_path')

    def handle(self, *args, **opts):
        path = opts['csv_path']
        created, updated = 0, 0
        with open(path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            required = {'username','role'}
            if not required.issubset(reader.fieldnames or []):
                raise CommandError(f"CSV must contain: {required}")

            for row in reader:
                username = (row.get('username') or '').strip()
                role = (row.get('role') or '').strip().lower()  # 'student' or 'staff'
                email = (row.get('email') or '').strip() or ''
                first_name = (row.get('first_name') or '').strip()
                last_name = (row.get('last_name') or '').strip()
                raw_password = (row.get('password') or '').strip()  # optional
                module_code = (row.get('module_code') or '').strip()  # for staff
                modules_csv = (row.get('modules') or '').strip()      # comma-separated for students

                if role not in ('student','staff') or not username:
                    self.stdout.write(self.style.WARNING(f"Skipping row: {row}"))
                    continue

                # create or update user
                user, was_created = User.objects.get_or_create(username=username, defaults={
                    'email': email, 'first_name': first_name, 'last_name': last_name, 'role': role
                })
                if not was_created:
                    user.email = email
                    user.first_name = first_name
                    user.last_name = last_name
                    user.role = role
                    user.save(update_fields=['email','first_name','last_name','role'])

                # set password (optional: only if provided or on create)
                if raw_password:
                    user.set_password(raw_password)
                    user.save(update_fields=['password'])
                elif was_created:
                    user.set_password(username)  # simple default; change as needed
                    user.save(update_fields=['password'])

                # attach modules
                if role == 'staff':
                    if module_code:
                        mod = Module.objects.filter(code=module_code).first()
                        if not mod:
                            self.stdout.write(self.style.WARNING(f"Unknown module_code {module_code} for {username}"))
                        else:
                            user.module = mod
                            user.save(update_fields=['module'])
                else:  # student
                    user.modules.clear()
                    if modules_csv:
                        codes = [c.strip() for c in modules_csv.split(',') if c.strip()]
                        mods = list(Module.objects.filter(code__in=codes))
                        user.modules.add(*mods)

                created += 1 if was_created else 0
                updated += 0 if was_created else 1

        self.stdout.write(self.style.SUCCESS(f"Users imported. created={created}, updated={updated}"))
