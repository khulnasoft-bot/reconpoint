# Generated manually for performance improvements

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scanEngine', '0001_initial'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='enginetype',
            index=models.Index(fields=['engine_name'], name='enginetype_engine_name_idx'),
        ),
        migrations.AddIndex(
            model_name='enginetype',
            index=models.Index(fields=['default_engine'], name='enginetype_default_engine_idx'),
        ),
    ]