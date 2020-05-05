from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
import os
import shutil
from .generate_image import generate_image_file
from django.forms.models import model_to_dict

from django.contrib.auth.models import User
from ..models import Images
from django.core.files.uploadedfile import SimpleUploadedFile

class SharedImagesTest(APITestCase):
    def setUp(self):
        """
        - Create 3 users (user1,2,3)
        - Create 1 img object for every user with sharing ({user1:[user2,user3],user2:[user1],user3:None})

        """
        self.url_uploads = reverse('fileupload')
        self.url_shared = reverse('shared_img')
        self.user_list = []
        #Create 3 users (user1,2,3)
        for user in range(1,4):
            created_user = User.objects.create_user(username=f'user{user}',
                                                  email=f'user{user}@email.com',
                                                  password='Test123456')
            self.user_list.append(created_user)
        self.user1,self.user2,self.user3 = self.user_list

        # Folder for saving test images
        current_path = os.path.abspath(os.getcwd()).replace('img_upload_api\\tests', '')
        self.test_pic_folder = current_path + '\\media\\testing_pics'

        #Create image objects with sharing
        # user1 = 1 (shared: user2,user3)
        # user2 = 1 (shared: user1)
        # user3 = 1 (shared: none)
        for count,user in enumerate(self.user_list,1):
            self.client.force_authenticate(user)
            img_file = generate_image_file(f'test{count}')
            #print(1)
            if count == 1: data = {'uploaded_image': img_file,'share_user':[self.user2.id,self.user3.id]}
            elif count == 2: data = {'uploaded_image': img_file,'share_user':self.user1.id}
            elif count == 3: data = {'uploaded_image': img_file}

            response = self.client.post(self.url_uploads, data, format='multipart')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)


    def test_share_users(self):
        '''
        Loop throught user list (3x user)
        - user have one image
        'uploads':
            - check if logged user is owner of image
            - check count of shared users for specific image
        'shared':
            - check owner of shared image
            - check if logged user is in list of shared users for showed image

        '''
        for user in self.user_list:
            self.client.force_authenticate(user)
            response = self.client.get(self.url_uploads, format='json')
            self.assertEqual(len(response.data), 1)
            self.assertEqual(response.data[0]['owner'], user.username)
            if user.username == 'user1': shared_user = 2
            elif user.username == 'user2': shared_user = 1
            elif user.username == 'user3': shared_user = 0
            #count of shared users for specific owner
            self.assertEqual(len(response.data[0]['share_user']), shared_user)
            #Get shared images
            response = self.client.get(self.url_shared, format='json')
            #every user have one shared image
            self.assertEqual(len(response.data), 1)

            #check owner of shared image
            #check if logged user is in list of shared for showed image
            if user.username == 'user1':
                self.assertEqual('user2',response.data[0]['owner'])
                self.assertIn(user.id, response.data[0]['share_user'])
            if user.username == 'user2':
                self.assertEqual('user1',response.data[0]['owner'])
                self.assertIn(user.id, response.data[0]['share_user'])
            if user.username == 'user3':
                self.assertEqual('user1',response.data[0]['owner'])
                self.assertIn(user.id, response.data[0]['share_user'])


    def test_update_share_user(self):
        """
        - edit user3 to share img with user1
        -
        """
        self.client.force_authenticate(self.user3)
        #get user3 image object and convert to dict
        #data = model_to_dict(Images.objects.get(id=3))
        data = {
            'favourite': False,
            'share_user':[self.user1.id]
        }

        url_upload_one = self.url_uploads + str(3)

        self.client.put(url_upload_one,data=data,format='json')

        #
        # self.assertIn(1,response.data['share_user'])
        #
        # self.client.force_authenticate(self.user1)
        # response = self.client.get(self.url_shared,format='json')
        # #user2 and user3 shared img with user1
        # self.assertEqual(len(response.data),2)
        # self.assertEqual(response.data[0]['owner'],'user2')
        # self.assertEqual(response.data[1]['owner'], 'user3')


    def tearDown(self):
        """
        Delete folder with testing pictures saved in 'media\testing_pics'
        """

        shutil.rmtree(self.test_pic_folder)

















