# Generated manually for performance improvements

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('targetApp', '0001_initial'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='domain',
            index=models.Index(fields=['name'], name='domain_name_idx'),
        ),
        migrations.AddIndex(
            model_name='domain',
            index=models.Index(fields=['project'], name='domain_project_idx'),
        ),
        migrations.AddIndex(
            model_name='domaininfo',
            index=models.Index(fields=['domain'], name='domaininfo_domain_idx'),
        ),
    ]