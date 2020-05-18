from django.core.management import call_command
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from django.urls import reverse
import os
from PIL import Image
from datetime import timedelta
from django.utils import timezone
import shutil
from .others import get_testing_media_path, create_testing_folder

from ..models import Images, StyleImage


class DeleteOldImagesTest(APITestCase):
    def setUp(self):
        """
        - create 1 user 'test_user'
        - generate and save 4 images to testing_pics folder
        - create 4 image objects and 4 style image objects
        - edit created date for each image objects. ages of img objects in days [1,5,24,40]
        - set favourite to True for objects which are old 1 and 24 days, for two remaining 5 and 40 days set favourite to False
        """
        current_path = os.path.abspath(os.getcwd()).replace("img_upload_api/tests", "")
        self.test_pic_folder = get_testing_media_path()

        self.url_upload = reverse("fileupload")
        # Create user for authentication
        user = User.objects.create_user(
            username="test_user", email="test@email.com", password="Test123456"
        )
        # Authenticate created test user
        self.client.force_authenticate(user)
        # create testing folder for saving images
        create_testing_folder()
        # create image file
        image = Image.new("RGBA", size=(150, 100), color=(155, 0, 0))
        # (50,70) styled images
        self.list_created_date_old_days = [1, 5, 25, 40]

        # create 4 image objects
        for count, days_from_created in enumerate(self.list_created_date_old_days):
            img_name = f"testcommand{count}.png"
            image_path = f"{self.test_pic_folder}/{img_name}"
            image.save(image_path)
            # For objects which are old 1 or 25 days set favourite=True, remain two objects (5 and 40 old days) set to False
            if days_from_created == 1 or days_from_created == 25:
                img_obj = Images.objects.create(
                    img_name=f"test{str(count)}",
                    owner=user,
                    uploaded_image=image_path,
                    favourite=True,
                )
            else:
                img_obj = Images.objects.create(
                    img_name=f"test{str(count)}",
                    owner=user,
                    uploaded_image=image_path,
                    favourite=False,
                )
            # Edit created_date
            calculated_date = timezone.now() - timedelta(days=days_from_created)
            img_obj.created_date = calculated_date
            img_obj.save()

        # create 4 style image objects
        for count, days_from_created in enumerate(self.list_created_date_old_days):
            original_image = Images.objects.get(id=1)
            img_name = f"testcommand_style{count}.png"
            image_path = f"{self.test_pic_folder}/{img_name}"
            image.save(image_path)
            # For objects which are old 1 or 25 days set favourite=True, remain two objects (5 and 40 old days) set to False
            if days_from_created == 1 or days_from_created == 25:
                img_obj = StyleImage.objects.create(
                    img_name=f"test{str(count)}",
                    owner=user,
                    styled_image=image_path,
                    favourite=True,
                    original_image=original_image,
                )
            else:
                img_obj = StyleImage.objects.create(
                    img_name=f"test{str(count)}",
                    owner=user,
                    styled_image=image_path,
                    favourite=False,
                    original_image=original_image,
                )
            # Edit created_date
            calculated_date = timezone.now() - timedelta(days=days_from_created)
            img_obj.created_date = calculated_date
            img_obj.save()

    def test_object_creating(self):
        # Check if objects was successfully created with corrects aging of days
        for count, obj in enumerate(Images.objects.all()):
            calculated_date = (timezone.now() - obj.created_date).days
            self.assertEqual(calculated_date, self.list_created_date_old_days[count])

    def test_delete_old_image_objects(self):
        """
        Apply for Images and StyleImages
        - Delete all image objects which are older then 14days AND favourite=False
        - Only object_id 4 should be delete (days old = 40, favourite = False)
        - Check if 3 remained objects are not older then 14 days or favourite = True
        """
        # Call command for deleting objects
        call_command("delete_old_images")
        self.assertEqual(len(Images.objects.all()), 3)
        self.assertEqual(len(Images.objects.filter(id=4)), 0)
        model_list = [Images, StyleImage]
        # Check if 3 remain objects are not older then 14 days or favourite field is set to True
        # Test for each model [Images,StyleImage]
        for model in model_list:
            self.assertEqual(len(model.objects.all()), 3)
            self.assertEqual(len(model.objects.filter(id=4)), 0)
            for obj in model.objects.all():
                calculated_date = (timezone.now() - obj.created_date).days
                self.assertTrue(calculated_date <= 14 or obj.favourite == True)

    def tearDown(self):
        """
        Delete folder with testing pictures saved in 'media\testing_pics'
        """
        shutil.rmtree(self.test_pic_folder)
