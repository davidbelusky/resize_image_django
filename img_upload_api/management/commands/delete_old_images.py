from django.core.management.base import BaseCommand
from img_upload_api.models import Images,StyleImage
from datetime import timedelta
from django.utils import timezone

class Command(BaseCommand):
    help = 'Delete image and style image objects which are older then 14 days and field favourite is set to False'
    def handle(self, *args, **options):
        """
        Delete image and style image objects which meet conditions below
        - older than 14 days
        - favourite = False
        """
        days_to_delete = 14
        calculated_date = timezone.now() - timedelta(days=days_to_delete)
        # get old images
        old_images = Images.objects.filter(created_date__lte=calculated_date, favourite=False)
        # get old style images
        old_images_styled = StyleImage.objects.filter(created_date__lte=calculated_date, favourite=False)
        # delete objects
        deleted_objects = old_images.delete()
        deleted_style_objects = old_images_styled.delete()

        return f'Deleted objects: {deleted_objects},Deleted style objects: {deleted_style_objects}'

