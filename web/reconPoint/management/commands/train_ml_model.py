from django.core.management.base import BaseCommand

from reconPoint.ml_utils import train_fp_model


class Command(BaseCommand):
    help = "Train the false positive detection model"

    def handle(self, *args, **options):
        train_fp_model()
        self.stdout.write(self.style.SUCCESS("Model trained successfully"))
