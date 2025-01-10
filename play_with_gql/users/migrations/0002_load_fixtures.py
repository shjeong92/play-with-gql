from django.core.management import call_command
from django.db import migrations


def load_user(apps, schema_editor):
    call_command("loaddata", "play_with_gql/users/fixtures/users.json")


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial')
    ]       

    operations = [
        migrations.RunPython(load_user)
    ]