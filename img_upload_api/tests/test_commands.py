from django.core.management import call_command
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from django.urls import reverse
import os
from PIL import Image
from datetime import timedelta
from django.utils import timezone
import shutil

from ..models import Images

class DeleteOldImagesTest(APITestCase):
    def setUp(self):
        """
        - create 1 user 'test_user'
        - generate and save 4 images to testing_pics folder
        - create 4 image objects
        - edit created date for each image objects. ages of img objects in days [1,5,24,40]
        - set favourite to True for objects which are old 1 and 24 days, for two remaining 5 and 40 days set favourite to False
        """
        self.current_path = os.path.abspath(os.getcwd()).replace('img_upload_api/tests', '')
        self.test_pic_folder = self.current_path + '/media/testing_pics'

        self.url_upload = reverse('fileupload')
        # Create user for authentication
        user = User.objects.create_user(username='test_user',
                                        email='test@email.com',
                                        password='Test123456')
        # Authenticate created test user
        self.client.force_authenticate(user)

        current_path = os.path.abspath(os.getcwd()).replace('img_upload_api/tests', '')
        self.test_pic_folder = current_path + '/media/testing_pics'
        #if media folder doesnt exist create it
        if not os.path.isdir(self.current_path + '/media'):
            os.mkdir(self.current_path + '/media')
        #create folder for testing images
        if not os.path.isdir(self.test_pic_folder):
            os.mkdir(self.test_pic_folder)
        #create image file
        image = Image.new('RGBA', size=(150, 100), color=(155, 0, 0))
        self.list_created_date_old_days = [1,5,25,40]
        #save 4 images to testing_pics folder
        #create 4 image objects
        for count,days_from_created in enumerate(self.list_created_date_old_days):
            img_name = f'testcommand{count}.png'
            image_path = f'{self.test_pic_folder}/{img_name}'
            image.save(image_path)
            #For objects which are old 1 or 25 days set favourite=True, remain two objects (5 and 40 old days) set to False
            if days_from_created == 1 or days_from_created == 25:
                img_obj = Images.objects.create(owner=user,uploaded_image=image_path,favourite=True)
            else:
                img_obj = Images.objects.create(owner=user, uploaded_image=image_path, favourite=False)
            #Edit created_date
            calculated_date = timezone.now() - timedelta(days=days_from_created)
            img_obj.created_date = calculated_date
            img_obj.save()

    def test_object_creating(self):
        #Check if objects was successfully created with corrects aging of days
        for count,obj in enumerate(Images.objects.all()):
            calculated_date = (timezone.now() - obj.created_date).days
            self.assertEqual(calculated_date,self.list_created_date_old_days[count])

    def test_delete_old_image_objects(self):
        """
        - Delete all image objects which are older then 14days AND favourite=False
        - Only object_id 4 should be delete (days old = 40, favourite = False)
        - Check if 3 remained objects are not older then 14 days or favourite = True
        """
        #Call command for deleting objects
        call_command('delete_old_images')
        self.assertEqual(len(Images.objects.all()),3)
        self.assertEqual(len(Images.objects.filter(id=4)),0)
        #Check if 3 remain objects are not older then 14 days or favourite field is set to True
        for obj in Images.objects.all():
            calculated_date = (timezone.now() - obj.created_date).days
            self.assertTrue(calculated_date <= 14 or obj.favourite == True)

    def tearDown(self):
        """
        Delete folder with testing pictures saved in 'media\testing_pics'
        """
        shutil.rmtree(self.test_pic_folder)