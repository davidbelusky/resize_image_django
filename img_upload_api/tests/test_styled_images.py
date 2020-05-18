from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
import os
import shutil

from django.contrib.auth.models import User
from ..models import Images
from .others import generate_image_file
from .others import get_testing_media_path


class Test_styled_images(APITestCase):
    def setUp(self):
        # Create users for authentication
        self.user = User.objects.create_user(
            username="test_user", email="test@email.com", password="Test123456"
        )
        self.user2 = User.objects.create_user(
            username="test_user2", email="test@email.com", password="Test123456"
        )

        # Authenticate created test user
        self.client.force_authenticate(self.user)

        self.url_styled = reverse("styled_images")
        self.url_images = reverse("fileupload")
        # Folder for saving test images
        self.test_pic_folder = get_testing_media_path()
        img_file = generate_image_file("test_original_img")
        data = {"img_name": "test_original_image", "uploaded_image": img_file}
        response = self.client.post(self.url_images, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_upload_styled_image(self):
        img_file = generate_image_file("test1")
        orig_img = Images.objects.get(id=1)
        data = {
            "img_name": "test_img1",
            "styled_image": img_file,
            "original_image": orig_img.id,
        }
        response = self.client.post(self.url_styled, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # check if styled_image file was created
        self.assertTrue(
            os.path.isfile(self.test_pic_folder + "/styled_images/test1.png")
        )

    def test_upload_style_image_wrong_input(self):
        """
        - try to stylize image where original image owner not equal to logged user
        """
        self.client.force_authenticate(self.user2)

        img_file = generate_image_file("test2")
        orig_img = Images.objects.get(id=1)
        data = {
            "img_name": "test_img2",
            "styled_image": img_file,
            "original_image": orig_img.id,
        }
        response = self.client.post(self.url_styled, data, format="multipart")
        # Try stylizing original image which owner is user1
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def tearDown(self):
        """
        Delete folder with testing pictures saved in 'media\testing_pics'
        """
        shutil.rmtree(self.test_pic_folder)
