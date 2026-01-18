# Generated manually for performance improvements

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recon_note', '0001_initial'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='todonote',
            index=models.Index(fields=['project'], name='todonote_project_idx'),
        ),
        migrations.AddIndex(
            model_name='todonote',
            index=models.Index(fields=['is_done'], name='todonote_is_done_idx'),
        ),
        migrations.AddIndex(
            model_name='todonote',
            index=models.Index(fields=['is_important'], name='todonote_is_important_idx'),
        ),
    ]