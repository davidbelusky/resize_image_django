from django.core.management.base import BaseCommand
from img_upload_api.models import Images
from datetime import timedelta
from django.utils import timezone
import os

class Command(BaseCommand):
    help = 'Delete image objects which are older then 14 days and field favourite is set to False'
    def handle(self, *args, **options):
        """
        Delete image objects which meet conditions below
        - older than 14 days
        - favourite = False
        """
        days_to_delete = 14
        calculated_date = timezone.now() - timedelta(days=days_to_delete)
        old_images = Images.objects.filter(created_date__lte=calculated_date,favourite=False)
        deleted_objects = old_images.delete()

        return f'Deleted objects: {deleted_objects}'
