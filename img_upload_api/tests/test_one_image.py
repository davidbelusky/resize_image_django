from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
import os
from django.forms.models import model_to_dict
from PIL import Image
import shutil
from django.contrib.auth.models import User

from .others import generate_image_file
from .others import get_testing_media_path
from ..models import Images


class Test_one_image(APITestCase):
    def setUp(self):
        self.url_name_one = "fileupload_one"
        # URL for posting images
        self.url_upload = reverse("fileupload")
        self.user1 = User.objects.create_user(
            username="user1", email="user1@email.com", password="Test123456"
        )

        self.user2 = User.objects.create_user(
            username="user2", email="user2@email.com", password="Test123456"
        )
        # Folder for saving test images
        self.test_pic_folder = get_testing_media_path()

        # Upload 1 image for user1
        self.client.force_authenticate(self.user1)
        img_file = generate_image_file("test")
        data = {"img_name": "test", "uploaded_image": img_file}
        response = self.client.post(self.url_upload, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Upload 2 images for user2
        self.client.force_authenticate(self.user2)
        for upload in range(2):
            img_file = generate_image_file(f"test{upload}")
            data = {"img_name": f"test{str(upload)}", "uploaded_image": img_file}
            response = self.client.post(self.url_upload, data, format="multipart")
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_owner_image(self):
        """
        - get image_id for specific user
        - user2 get image which owner is user1 (not allowed)
        """

        # user1 is owner of image_id 1
        # user2 is owner of image ids (2,3)
        for image_id in range(1, 4):
            url = reverse(self.url_name_one, args=(image_id,))
            if image_id == 1:
                self.client.force_authenticate(self.user1)
            else:
                self.client.force_authenticate(self.user2)

            response = self.client.get(url, format="json")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            if image_id == 1:
                self.assertEqual(response.data["owner"], "user1")
            else:
                self.assertEqual(response.data["owner"], "user2")

        # user2 try to get image_id 1 which is owner user1
        url = reverse(self.url_name_one, args=(1,))
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_edit_image_instance(self):
        """
        - edit image_id 1,owner user1
        - edit to {'img_name':'photo_user1','img_description':'photo of user1',
                'favourite':True,'width':700,'height':500}
        - check if all fields was successfully edited
        - check if image was resized to a new edited sizes
        """
        self.client.force_authenticate(self.user1)
        data = {
            "img_name": "photo_user1",
            "img_description": "photo of user1",
            "favourite": True,
            "width": 700,
            "height": 500,
            "share_user": [],
        }
        url = reverse(self.url_name_one, args=(1,))
        response = self.client.put(url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Get edited object, convert to dict and compare with inputs
        obj = model_to_dict(Images.objects.get(id=1))
        for field, edited_data in data.items():
            self.assertEqual(edited_data, obj[field])
        # Check if image was edited to a new input
        edited_img = Image.open(self.test_pic_folder + "/test.png")
        self.assertEqual(edited_img.size, (700, 500))

    def tearDown(self):
        """
        Delete folder with testing pictures saved in 'media\testing_pics'
        """
        shutil.rmtree(self.test_pic_folder)
