from django.db.models.signals import post_save
from django.dispatch import receiver

from reconPoint.celery import app
from startScan.models import ScanHistory


@receiver(post_save, sender=ScanHistory)
def scan_completed_signal(sender, instance, **kwargs):
    if instance.scan_status == 2:  # Assuming 2 is completed
        # Emit event for downstream processing
        app.send_task("reconPoint.tasks.handle_scan_completion", args=[instance.id])


# Celery signal for task success
from celery.signals import task_success


@task_success.connect
def task_success_handler(sender=None, result=None, **kwargs):
    print(f"Task {sender} succeeded with result {result}")
    # Could trigger next steps here
