from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
import shutil

from django.contrib.auth.models import User
from .generate_image import generate_image_file
from .others import get_testing_media_path

class Test_show_favourite_images(APITestCase):
    def setUp(self):
        """
        - create 2 users (test_user,test_user2)
        - test_user have 2 image objects one with set favourite field to True
        - test_user2 have 1 image object where favourite = False
        """
        #Create user for authentication
        self.user1 = User.objects.create_user(username='test_user',
                                             email='test@email.com',
                                             password='Test123456')
        self.user2 = User.objects.create_user(username='test_user2',
                                        email='test@email.com',
                                        password='Test123456')

        self.url_upload = reverse('fileupload')
        self.url_favourite = reverse('favourite_img')
        #Folder for saving test images
        self.test_pic_folder = get_testing_media_path()

        self.client.force_authenticate(self.user1)

        for count in range(3):
            img_file = generate_image_file(f'test{str(count)}')
            if count == 1: favourite = True
            else: favourite = False
            data = {
                'img_name':f'test{str(count)}',
                'uploaded_image': img_file,
                'favourite':favourite
            }
            if count == 2: self.client.force_authenticate(self.user2)
            response = self.client.post(self.url_upload, data, format='multipart')
            self.assertEqual(response.status_code,status.HTTP_201_CREATED)

    def test_favourite_show(self):
        """
        - check user1 have 2 img objects
        - check user1 have 1 favourite img object
        - check user1 favourite object have set field 'favourite' to True
        - check user2 have 1 img objects
        - check user2 dont have any favourite img object
        """
        self.client.force_authenticate(self.user1)

        response = self.client.get(self.url_upload, format='multipart')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(len(response.data),2)

        response_favourite = self.client.get(self.url_favourite, format='multipart')
        self.assertEqual(response_favourite.status_code,status.HTTP_200_OK)
        self.assertEqual(len(response_favourite.data['images']),1)
        #Check if showed favourite img have set field favourite to True
        self.assertTrue(response_favourite.data['images'][0]['favourite'])


        self.client.force_authenticate(self.user2)
        response = self.client.get(self.url_upload, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertFalse(response.data[0]['favourite'])
        response_favourite = self.client.get(self.url_favourite, format='multipart')
        self.assertEqual(response_favourite.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_favourite.data['images']), 0)

    def tearDown(self):
        """
        Delete folder with testing pictures saved in 'media\testing_pics'
        """
        shutil.rmtree(self.test_pic_folder)