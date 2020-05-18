from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
import shutil
from PIL import Image

from django.contrib.auth.models import User
from .others import get_testing_media_path, create_testing_folder
from ..models import Images, StyleImage


class Test_show_favourite_images(APITestCase):
    def setUp(self):
        """
        - create 2 users (test_user,test_user2)
        - test_user have 2 image objects one with set favourite field to True
        - test_user2 have 1 image object where favourite = False
        """
        # Create user for authentication
        self.user1 = User.objects.create_user(
            username="test_user", email="test@email.com", password="Test123456"
        )
        self.user2 = User.objects.create_user(
            username="test_user2", email="test@email.com", password="Test123456"
        )

        self.url_images = reverse("fileupload")
        self.url_styleimages = reverse("styled_images")
        self.url_favourite = reverse("favourite_img")
        # Folder for saving test images
        self.test_pic_folder = get_testing_media_path()

        image = Image.new("RGBA", size=(150, 100), color=(155, 0, 0))
        # create testing folder for saving images
        create_testing_folder()
        # create 4 Images objects
        for count in range(1, 4):
            img_name = f"test_favourite_img{count}.png"
            image_path = f"{self.test_pic_folder}/{img_name}"
            image.save(image_path)

            if count == 2:
                favourite = True
            else:
                favourite = False
            if count == 3:
                user = self.user2
            else:
                user = self.user1
            Images.objects.create(
                img_name=f"test{str(count)}",
                owner=user,
                uploaded_image=image_path,
                favourite=favourite,
            )
        # create 4 StyleImages objects
        for count in range(1, 4):
            img_name = f"test_favourite_img_style{count}.png"
            image_path = f"{self.test_pic_folder}/{img_name}"
            image.save(image_path)

            if count == 2:
                favourite = True
            else:
                favourite = False
            if count == 3:
                user = self.user2
                original_image = Images.objects.get(id=3)
            else:
                user = self.user1
                original_image = Images.objects.get(id=1)
            StyleImage.objects.create(
                img_name=f"test_style{str(count)}",
                owner=user,
                styled_image=image_path,
                favourite=favourite,
                original_image=original_image,
            )
        # Check if both models have 3 objects
        self.assertEqual(len(StyleImage.objects.all()), 3)
        self.assertEqual(len(Images.objects.all()), 3)

    def test_favourite_images(self):
        """
        Check for both models [Images,StyleImage]
        - user1 have 2 img objects
        - user1 have 1 favourite img object
        - user1 favourite object have set field 'favourite' to True
        - user2 have 1 img objects
        - user2 dont have any favourite img object
        """
        self.client.force_authenticate(self.user1)
        # User1 have 2 Images and 2 StyleImages
        url_images_list = [self.url_images, self.url_styleimages]
        for url_img in url_images_list:
            response = self.client.get(url_img, format="multipart")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data), 2)
        # User1 have 1 Image and 1 StyleImaged marked as favourite
        response_favourite = self.client.get(self.url_favourite, format="multipart")
        self.assertEqual(response_favourite.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_favourite.data["images"]), 1)
        self.assertEqual(len(response_favourite.data["styled_images"]), 1)
        # Check if showed favourite img have set field favourite to True
        self.assertTrue(response_favourite.data["images"][0]["favourite"])
        self.assertTrue(response_favourite.data["styled_images"][0]["favourite"])

        self.client.force_authenticate(self.user2)
        # User2 have 1 Image and 1 StyleImage
        for url_img in url_images_list:
            response = self.client.get(url_img, format="multipart")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data), 1)
            self.assertFalse(response.data[0]["favourite"])
        # User2 dont have any favourite Image or StyleImage
        response_favourite = self.client.get(self.url_favourite, format="multipart")
        self.assertEqual(response_favourite.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_favourite.data["images"]), 0)
        self.assertEqual(len(response_favourite.data["styled_images"]), 0)

    def tearDown(self):
        """
        Delete folder with testing pictures saved in 'media\testing_pics'
        """
        shutil.rmtree(self.test_pic_folder)
