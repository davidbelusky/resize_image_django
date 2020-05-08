from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
import os
import shutil
from .generate_image import generate_image_file

from django.contrib.auth.models import User
from ..models import Images

def filter_generate(**kwargs):
    """
    Generate filter URL parameters for URL
    key = filter ex.(exchange_id__id,exchange_id__name)
    value = filtered value ex.(2,'David')
    ex. filter_generate(exchange_id__id=2,exchange_id__name='David')
    Return: filter parameters ex. (?exchange_id__id=2&exchange_id__name__iexact=David&)
    """
    #Filters begin with '?'
    final_filter = '?'
    for k,v in kwargs.items():
        filter_url = '{filter}={value}&'.format(filter=k,value=v)
        final_filter += filter_url

    return final_filter

class UploadsFilterTest(APITestCase):
    def setUp(self):
        self.url = reverse('fileupload')
        self.user1 = User.objects.create_user(username='user1',
                                              email='user1@email.com',
                                              password='Test123456')

        self.user2 = User.objects.create_user(username='user2',
                                              email='user2@email.com',
                                              password='Test123456')
        # Folder for saving test images
        current_path = os.path.abspath(os.getcwd()).replace('img_upload_api/tests', '')
        self.test_pic_folder = current_path + '/media/testing_pics'

        #user1 = 3 images, user2 = 2 images
        for upload in range(1,6):
            if upload <= 3:
                self.client.force_authenticate(self.user1)
            else:
                self.client.force_authenticate(self.user2)
            img_file = generate_image_file(f'test{upload}')
            data = {
                'uploaded_image': img_file
            }
            response = self.client.post(self.url, data, format='multipart')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_filter_search_user1(self):
        '''
        searching applied only for 'img_name' field (case insensitive,startswith)
        - check user1 count of object (3)
        - case insensitive search 'Test1'
        - test startswith search 'test' return 3 objects
        - search non exist object
        - try to filter img objects of not logged user
        '''
        self.client.force_authenticate(self.user1)
        response = self.client.get(self.url,format='json')
        self.assertEqual(len(response.data),3)

        #Search is case insensitive
        #Filter img_name startwith 'Test1'
        filters = filter_generate(search='Test1')
        url_filter = self.url + filters
        response = self.client.get(url_filter,format='json')
        #1 img with name 'Test1'
        self.assertEqual(len(response.data),1)
        self.assertEqual(response.data[0]['img_name'],'test1')

        #Filter img_name startwith 'test'
        filters = filter_generate(search='test')
        url_filter = self.url + filters
        response = self.client.get(url_filter,format='json')
        #3 images start with img name 'test'
        self.assertEqual(len(response.data), 3)
        #All 3 objects start with searched img_name 'test' (test1,test2,test3)
        for img_object in response.data:
            self.assertTrue(img_object['img_name'].startswith('test'))
            self.assertEqual(img_object['owner'], 'user1')

        #Find non exist img_name
        filters = filter_generate(search='abcd')
        url_filter = self.url + filters
        response = self.client.get(url_filter, format='json')
        self.assertEqual(len(response.data),0)

        #Get user2 image object (authenticated user1)
        filters = filter_generate(search='test4')
        url_filter = self.url + filters
        response = self.client.get(url_filter, format='json')
        self.assertEqual(len(response.data),0)

        #Get user2 image object (authenticated user2)
        self.client.force_authenticate(self.user2)
        response = self.client.get(url_filter, format='json')
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['owner'],'user2')

        #Get all user2 objects startswith 'test'
        filters = filter_generate(search='test')
        url_filter = self.url + filters
        response = self.client.get(url_filter, format='json')
        self.assertEqual(len(response.data), 2)
        for img_object in response.data:
            self.assertTrue(img_object['img_name'].startswith('test'))
            self.assertEqual(img_object['owner'],'user2')


    def tearDown(self):
        """
        Delete folder with testing pictures saved in 'media\testing_pics'
        """
        shutil.rmtree(self.test_pic_folder)





