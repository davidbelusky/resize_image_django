from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from PIL import Image
import os
import shutil
from django.contrib.auth.models import User

from .others import generate_image_file
from .others import get_testing_media_path


class Test_image_resize_upload(APITestCase):
    def setUp(self):
        # Create user for authentication
        user = User.objects.create_user(
            username="test_user", email="test@email.com", password="Test123456"
        )
        # Authenticate created test user
        self.client.force_authenticate(user)

        self.url = reverse("fileupload")
        # Folder for saving test images
        self.test_pic_folder = get_testing_media_path()

    def test_upload_image_without_size(self):
        """
        Upload image without inputed size
        If width and height was not inputted upload img without changing size

        - Input img width = 150, height = 100
        - Check if uploaded img have same size as inputted
        """

        img_file = generate_image_file("test1")

        data = {"img_name": "test1", "uploaded_image": img_file}

        response = self.client.post(self.url, data, format="multipart")
        response_data = response.data
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual([response_data["width"], response_data["height"]], [150, 100])
        # open resized image
        resized_img = Image.open(self.test_pic_folder + "/test1.png")
        self.assertEqual(resized_img.size, (150, 100))

    def test_upload_image_with_height(self):
        """
        Input only height ex. {'uploaded_image':test2.png,'height':400}
        Create img width=150, height=100
        Input: height=400
        Resize to: width=150,height=400
        """

        file_name = "test2"
        img_file = generate_image_file(file_name)

        data = {"img_name": "test2", "uploaded_image": img_file, "height": 400}

        response = self.client.post(self.url, data, format="multipart")
        response_data = response.data
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual([response_data["width"], response_data["height"]], [150, 400])
        # check resized image
        resized_img = Image.open(self.test_pic_folder + f"/{file_name}.png")
        self.assertEqual(resized_img.size, (150, 400))

    def test_upload_image_with_width(self):
        """
        Input only width ex. {'uploaded_image':test3.png,'width':300}
        Create img width=150, height=100
        Input: width=300
        Resize to: width=300,height=100
        """

        file_name = "test3"
        img_file = generate_image_file(file_name)

        data = {"img_name": "test3", "uploaded_image": img_file, "width": 300}

        response = self.client.post(self.url, data, format="multipart")
        response_data = response.data
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual([response_data["width"], response_data["height"]], [300, 100])
        # check resized image
        resized_img = Image.open(self.test_pic_folder + f"/{file_name}.png")
        self.assertEqual(resized_img.size, (300, 100))

    def test_upload_image_size_in_maxlimit(self):
        """
        Input with width and height ex. {'uploaded_image':test4.png,'width':750,'height':600}
        Create img width=150, height=100
        Input: width=750, height=600
        Resize to: width=750, height=600
        """
        input_width = 750
        input_height = 600

        file_name = "test4"
        img_file = generate_image_file(file_name)

        data = {
            "img_name": "test4",
            "uploaded_image": img_file,
            "width": input_width,
            "height": input_height,
        }

        response = self.client.post(self.url, data, format="multipart")
        response_data = response.data
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            [response_data["width"], response_data["height"]],
            [input_width, input_height],
        )
        # check resized image
        resized_img = Image.open(self.test_pic_folder + f"/{file_name}.png")
        self.assertEqual(resized_img.size, (input_width, input_height))

    def test_upload_image_size_over_maxlimit(self):
        """
        Max limits: width = 1920, height = 1080
        Input with width and height ex. {'uploaded_image':test5.png,'width':2300,'height':1700}
        Create img width=150, height=100
        Input: width=2300, height=1700
        Resize to: width=1920, height=1080 (maximum allowed size)

        Check if image was resized to maximum allowed size
        """
        input_width = 2300
        input_height = 1700
        max_width = 1920
        max_height = 1080

        file_name = "test5"
        img_file = generate_image_file(file_name)

        data = {
            "img_name": "test5",
            "uploaded_image": img_file,
            "width": input_width,
            "height": input_height,
        }

        response = self.client.post(self.url, data, format="multipart")
        response_data = response.data
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            [response_data["width"], response_data["height"]], [max_width, max_height]
        )
        # check resized image
        resized_img = Image.open(self.test_pic_folder + f"/{file_name}.png")
        self.assertEqual(resized_img.size, (max_width, max_height))

    def test_name_and_ext_image_default(self):
        """
        - Test object create success
        - image_name not inputted set to original image name (test6)
        - save image extension format (png)
        - default favorite boolean set to False
        """
        file_name = "test6"
        img_file = generate_image_file(file_name)

        data = {"img_name": "test6", "uploaded_image": img_file}
        response = self.client.post(self.url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # image name set to original file name
        self.assertEqual(response.data["img_name"], "test6")
        self.assertEqual(response.data["img_format"], "png")
        self.assertEqual(response.data["favourite"], False)
        self.assertEqual(response.data["img_description"], "")

    def test_name_and_ext_image_inputs(self):
        """
        - Test object create success
        - image_name set to ('david)
        - save image extension format (png)
        - img_description set to ('abcd')
        - favourite set to True
        """
        file_name = "test7"
        img_file = generate_image_file(file_name)

        data = {
            "img_name": "david",
            "img_description": "abcd",
            "favourite": True,
            "uploaded_image": img_file,
        }
        response = self.client.post(self.url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # image name set to original file name
        self.assertEqual(response.data["img_name"], "david")
        self.assertEqual(response.data["img_format"], "png")
        self.assertEqual(response.data["favourite"], True)
        self.assertEqual(response.data["img_description"], "abcd")

    def tearDown(self):
        """
        Delete folder with testing pictures saved in 'media\testing_pics'
        """
        shutil.rmtree(self.test_pic_folder)
