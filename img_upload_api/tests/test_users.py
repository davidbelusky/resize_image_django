from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
import shutil
import os
from django.contrib.auth.models import User

from .others import get_testing_media_path
from .generate_image import generate_image_file


class Test_register_user(APITestCase):
    def setUp(self):
        self.url = reverse('register_user')
        self.url_uploads = reverse('fileupload')

    def test_register_user_correct_input(self):
        '''
        - register new user
        - response after successfully register new user must be only 'username','email'
        - test login new user
        '''

        data = {
            'username':'david',
            'email':'david@email.com',
            'password':'Test123456',
            'password2':'Test123456'
        }
        response = self.client.post(self.url, data,format='json')
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
        #Return only username, email information
        correct_response_data_keys = ['username','email']
        self.assertEqual(correct_response_data_keys,list(response.data.keys()))

        self.client.login(username='david', password='Test123456')
        response_get = self.client.get(self.url_uploads,format='json')
        #Successfuly authenticate
        self.assertEqual(response_get.status_code,status.HTTP_200_OK)
        # 0 created objects for user 'david'
        self.assertEqual(len(response_get.data),0)

    def test_register_user_incorrect_input(self):
        # Password cannot be only numerical
        data = {
            'username': 'david',
            'email': 'david@email.com',
            'password': '123456789',
            'password2': '123456789'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Min length of password = 5
        data['password'] = 'Ab12'
        data['password2'] = 'Ab12'
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        #Password and Password2 must be same
        data['password'] = 'Test123456'
        data['password2'] = 'Test123457'
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        #Email must be in mail format test@mail.com
        data['password'] = 'Test123456'
        data['password2'] = 'Test123456'
        data['email'] = 'abcde'
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class Test_user_login(APITestCase):
    def setUp(self):
        self.url = reverse('fileupload')
        self.user1 = User.objects.create_user(username='user1',
                                        email='user1@email.com',
                                        password='Test123456')

        self.user2 = User.objects.create_user(username='user2',
                                         email='user2@email.com',
                                         password='Test123456')
        # Folder for saving test images
        self.test_pic_folder = get_testing_media_path

        # Upload 1 image for user1
        self.client.force_authenticate(self.user1)
        img_file = generate_image_file('test')
        data = {
            'img_name':'test',
            'uploaded_image': img_file
        }

        response = self.client.post(self.url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Upload 2 images for user2
        self.client.force_authenticate(self.user2)
        for upload in range(2):
            img_file = generate_image_file(f'test{upload}')
            data = {
                'img_name': f'test{str(upload)}',
                'uploaded_image': img_file
            }
            response = self.client.post(self.url, data, format='multipart')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_isowner(self):
        """
        - GET return 2 objects for user2
        - GET return 1 object for user1

        """
        #Authenticated user2
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        #Return 2 images for user2
        self.assertEqual(len(response.data),2)
        for object in response.data:
            self.assertEqual(object['owner'],'user2')

        #Authenticate user1
        self.client.force_authenticate(self.user1)
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Return 1 image for user1
        self.assertEqual(len(response.data), 1)
        for object in response.data:
            self.assertEqual(object['owner'], 'user1')

    def tearDown(self):
        """
        Delete folder with testing pictures saved in 'media\testing_pics'
        """
        shutil.rmtree(self.test_pic_folder)







