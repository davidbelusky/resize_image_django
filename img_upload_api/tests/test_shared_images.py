from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from PIL import Image
import shutil
from django.contrib.auth.models import User

from .others import get_testing_media_path, create_testing_folder
from ..models import Images, StyleImage


class SharedImagesTest(APITestCase):
    def setUp(self):
        """
        Apply to Images and StyleImages
        - Create 3 users (user1,2,3)
        - Create 1 img object for every user with sharing ({user1:[user2,user3],user2:[user1],user3:None})
        """
        self.url_images = reverse("fileupload")
        self.url_imagestyle = reverse("styled_images")
        self.url_shared = reverse("shared_img")
        self.user_list = []
        # Create 3 users (user1,2,3)
        for user in range(1, 4):
            created_user = User.objects.create_user(
                username=f"user{user}",
                email=f"user{user}@email.com",
                password="Test123456",
            )
            self.user_list.append(created_user)
        self.user1, self.user2, self.user3 = self.user_list

        # Folder for saving test images
        self.test_pic_folder = get_testing_media_path()

        image = Image.new("RGBA", size=(150, 100), color=(155, 0, 0))
        create_testing_folder()
        # Create image objects with sharing
        # user1 = 1 (shared: user2,user3)
        # user2 = 1 (shared: user1)
        # user3 = 1 (shared: none)
        for count, user in enumerate(self.user_list, 1):
            img_name = f"test_shared_img{count}.png"
            image_path = f"{self.test_pic_folder}/{img_name}"
            image.save(image_path)
            if count == 1:
                shared_user_list = [self.user2.id, self.user3.id]
            if count == 2:
                shared_user_list = [self.user1.id]
            if count == 3:
                shared_user_list = ""
            img_object = Images.objects.create(
                img_name=f"test{str(count)}", owner=user, uploaded_image=image_path
            )
            img_object.save()
            for share_user_add in shared_user_list:
                img_object.share_user.add(share_user_add)
                img_object.save()
        self.assertEqual(len(Images.objects.all()), 3)

        # Create styled images with sharing (same as for Images)
        for count, user in enumerate(self.user_list, 1):
            original_image = Images.objects.get(owner=user)
            img_name = f"test_shared_img_styled{count}.png"
            image_path = f"{self.test_pic_folder}/{img_name}"
            image.save(image_path)
            if count == 1:
                shared_user_list = [self.user2.id, self.user3.id]
            if count == 2:
                shared_user_list = [self.user1.id]
            if count == 3:
                shared_user_list = ""
            img_object = StyleImage.objects.create(
                img_name=f"test_style{str(count)}",
                owner=user,
                styled_image=image_path,
                original_image=original_image,
            )
            img_object.save()
            for share_user_add in shared_user_list:
                img_object.share_user.add(share_user_add)
                img_object.save()
        self.assertEqual(len(StyleImage.objects.all()), 3)

    def test_share_users(self):
        """
        Test for models [Images,StyledImage]
        Loop throught user list (3x user)
        - each user have one image
        'images':
            - check if logged user is owner of image
            - check count of shared users for specific image
        'shared_images':
            - check owner of shared image
            - check if logged user is in list of shared users for showed image

        """
        # dict_keys = key of responsed json in 'shared_images' ex. {'images':[object1,object2],'styled_images':[styled_object1,styled_object2]}
        models_dict = {
            "Images": {"url": self.url_images, "dict_key": "images"},
            "StyleImages": {"url": self.url_imagestyle, "dict_key": "styled_images"},
        }
        for model, values in models_dict.items():
            for user in self.user_list:
                self.client.force_authenticate(user)
                response = self.client.get(values["url"], format="json")
                self.assertEqual(len(response.data), 1)
                self.assertEqual(response.data[0]["owner"], user.username)
                if user.username == "user1":
                    shared_user = 2
                elif user.username == "user2":
                    shared_user = 1
                elif user.username == "user3":
                    shared_user = 0
                # count of shared users for specific owner
                self.assertEqual(len(response.data[0]["share_user"]), shared_user)
                # Get shared images
                response = self.client.get(self.url_shared, format="json")
                # every user have one shared image
                self.assertEqual(len(response.data[values["dict_key"]]), 1)

                # check owner of shared image
                # check if logged user is in list of shared for showed image
                if user.username == "user1":
                    self.assertEqual(
                        "user2", response.data[values["dict_key"]][0]["owner"]
                    )
                    self.assertIn(
                        user.id, response.data[values["dict_key"]][0]["share_user"]
                    )
                if user.username == "user2":
                    self.assertEqual(
                        "user1", response.data[values["dict_key"]][0]["owner"]
                    )
                    self.assertIn(
                        user.id, response.data[values["dict_key"]][0]["share_user"]
                    )
                if user.username == "user3":
                    self.assertEqual(
                        "user1", response.data[values["dict_key"]][0]["owner"]
                    )
                    self.assertIn(
                        user.id, response.data[values["dict_key"]][0]["share_user"]
                    )

    def test_update(self):
        self.client.force_authenticate(self.user3)
        data = {"img_name": "test_edit", "share_user": [1]}
        url = reverse("fileupload_one", args=(3,))
        response = self.client.put(url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check if user3 share img with user1
        self.client.force_authenticate(self.user1)
        response = self.client.get(self.url_shared, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        # user3 and user2 shared images with user1
        for obj in response.data["images"]:
            self.assertTrue(obj["owner"] == "user3" or obj["owner"] == "user2")
        for obj in response.data["styled_images"]:
            self.assertTrue(obj["owner"] == "user3" or obj["owner"] == "user2")

    def tearDown(self):
        """
        Delete folder with testing pictures saved in 'media\testing_pics'
        """
        shutil.rmtree(self.test_pic_folder)
