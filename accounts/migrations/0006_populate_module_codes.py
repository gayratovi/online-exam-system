from django.db import migrations

def populate_codes(apps, schema_editor):
    Module = apps.get_model('accounts', 'Module')
    for m in Module.objects.all().order_by('id'):
        if not m.code:
            m.code = f"MOD{m.id:03d}"   # e.g., MOD001, MOD002, …
            m.save(update_fields=['code'])

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_customuser_modules_module_code_and_more'),
    ]

    operations = [
        migrations.RunPython(populate_codes, migrations.RunPython.noop),
    ]
