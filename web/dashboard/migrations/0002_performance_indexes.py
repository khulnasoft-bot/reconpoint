# Generated manually for performance improvements

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='project',
            index=models.Index(fields=['name'], name='project_name_idx'),
        ),
        migrations.AddIndex(
            model_name='project',
            index=models.Index(fields=['slug'], name='project_slug_idx'),
        ),
    ]