# betatrax/migrations/0002_create_groups.py
from django.db import migrations

def create_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    for name in ['ProductOwner', 'Developer', 'BetaTester']:
        Group.objects.get_or_create(name=name)

class Migration(migrations.Migration):
    dependencies = [('betatrax', '0001_initial')]
    operations = [migrations.RunPython(create_groups)]
