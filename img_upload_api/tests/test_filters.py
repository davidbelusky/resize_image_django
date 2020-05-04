from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
import os
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
        current_path = os.path.abspath(os.getcwd()).replace('img_upload_api\\tests', '')
        self.test_pic_folder = current_path + '\\media\\testing_pics'

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

    def test_filter_search(self):
        self.client.force_authenticate(self.user1)
        response = self.client.get(self.url,format='json')
        self.assertEqual(len(response.data),3)
        filters = filter_generate(search='Test1')
        url_filter = self.url + filters
        print(url_filter)
        response = self.client.get(url_filter,format='json')
        print(response.data)
