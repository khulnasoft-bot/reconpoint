# Generated manually for performance improvements

from django.db import migrations, models
import django.contrib.postgres.indexes


class Migration(migrations.Migration):

    dependencies = [
        ('startScan', '0001_initial'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='subdomain',
            index=models.Index(fields=['name'], name='subdomain_name_idx'),
        ),
        migrations.AddIndex(
            model_name='subdomain',
            index=models.Index(fields=['target_domain'], name='subdomain_target_domain_idx'),
        ),
        migrations.AddIndex(
            model_name='subdomain',
            index=models.Index(fields=['scan_history'], name='subdomain_scan_history_idx'),
        ),
        migrations.AddIndex(
            model_name='subdomain',
            index=models.Index(fields=['http_status'], name='subdomain_http_status_idx'),
        ),
        migrations.AddIndex(
            model_name='endpoint',
            index=models.Index(fields=['http_url'], name='endpoint_http_url_idx'),
        ),
        migrations.AddIndex(
            model_name='endpoint',
            index=models.Index(fields=['subdomain'], name='endpoint_subdomain_idx'),
        ),
        migrations.AddIndex(
            model_name='endpoint',
            index=models.Index(fields=['scan_history'], name='endpoint_scan_history_idx'),
        ),
        migrations.AddIndex(
            model_name='endpoint',
            index=models.Index(fields=['http_status'], name='endpoint_http_status_idx'),
        ),
        migrations.AddIndex(
            model_name='vulnerability',
            index=models.Index(fields=['severity'], name='vulnerability_severity_idx'),
        ),
        migrations.AddIndex(
            model_name='vulnerability',
            index=models.Index(fields=['scan_history'], name='vulnerability_scan_history_idx'),
        ),
        migrations.AddIndex(
            model_name='vulnerability',
            index=models.Index(fields=['type'], name='vulnerability_type_idx'),
        ),
        migrations.AddIndex(
            model_name='scanhistory',
            index=models.Index(fields=['domain'], name='scanhistory_domain_idx'),
        ),
        migrations.AddIndex(
            model_name='scanhistory',
            index=models.Index(fields=['scan_status'], name='scanhistory_scan_status_idx'),
        ),
        migrations.AddIndex(
            model_name='scanhistory',
            index=models.Index(fields=['start_scan_date'], name='scanhistory_start_scan_date_idx'),
        ),
    ]