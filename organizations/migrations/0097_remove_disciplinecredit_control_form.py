from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0096_auto_20200129_1527'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='disciplinecredit',
            name='control_form',
        ),
    ]
