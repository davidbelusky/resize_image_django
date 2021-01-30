from django.db import models
from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser

from .ai_models.image_style_transfer import Transfer_Style_Image
from .others.resize_image import Resize_image
from django.utils.translation import ugettext_lazy as _

# Paths for saving orig images,style images and styled images
def owner_directory_path(instance, filename):
    # Image upload to media/pics/owner_{owner_id}/
    return f"pics/owner_{instance.owner.id}/{filename}"


def owner_directory_path_styles(instance, filename):
    # Styled image upload to media/pics/owner_{owner_id}/styles/
    return f"pics/owner_{instance.owner.id}/styled_images/{filename}"



class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_active", False)

        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)

class User(AbstractUser):
    username = None
    email = models.EmailField(_("email address"), unique=True)

    can_manage_users = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

class Images(models.Model):
    img_name = models.CharField(max_length=25, blank=False, null=False)
    img_description = models.TextField(max_length=50, blank=True)
    img_format = models.CharField(max_length=5)  # ex.(jpg,png)

    created_date = models.DateTimeField(auto_now_add=True)
    favourite = models.BooleanField(default=False)
    # If testing run save tested pics to 'testing_pics/'
    if settings.TESTING:
        uploaded_image = models.ImageField(
            blank=False, null=False, upload_to="testing_pics/"
        )
    # Normal run save pics to 'pics/'
    else:
        uploaded_image = models.ImageField(
            blank=False, null=False, upload_to=owner_directory_path
        )
    width = models.IntegerField(default=0)
    height = models.IntegerField(default=0)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    share_user = models.ManyToManyField(
        User, related_name="shared_user", blank=True, null=True
    )

    def __str__(self):
        # ex. "owner: david, img_name: first_image"
        return f"owner: {self.owner}, img_name: {self.img_name}"

    def save(self, *args, **kwargs):
        """
        - Automatically get image format from img path
        - Resize image before upload to DB
        - Save original size of image to media/pics
        - Replace original image with resized image
        """
        # Get img format ex.(jpg,png...)
        self.img_format = str(self.uploaded_image).split(".")[-1]
        # Resize image and return resized height,width and resized image
        self.height, self.width, resized_img = Resize_image.resizing(
            self.uploaded_image, self.height, self.width
        )
        # Save original size of image
        super().save(*args, **kwargs)
        # Replace original img with resized img
        resized_img.save(self.uploaded_image.path)


class StyleImage(models.Model):
    img_name = models.CharField(max_length=25, blank=False, null=False)
    if settings.TESTING:
        styled_image = models.ImageField(
            blank=False, null=False, upload_to="testing_pics/styled_images"
        )
    else:
        styled_image = models.ImageField(
            blank=False, null=False, upload_to=owner_directory_path_styles
        )
    img_description = models.TextField(max_length=250, blank=True)
    img_format = models.CharField(max_length=5)  # ex.(jpg,png)

    created_date = models.DateTimeField(auto_now_add=True)
    original_image = models.ForeignKey(Images, null=True, on_delete=models.SET_NULL)
    favourite = models.BooleanField(default=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    share_user = models.ManyToManyField(
        User, related_name="shared_user_styled", blank=True, null=True
    )

    def __str__(self):
        # ex. "owner: david, img_name: first_image"
        return f"owner: {self.owner}, img_name: {self.img_name}"

    def save(self, *args, **kwargs):
        """
        - before stylizing image check if 'pk' = None. If pk = None it means this image is posting first time so apply stylizing for this image
          if 'pk' != None mean image is already in DB and this action editing image fields. Dont apply stylizing for image
        - stylize original image with uploaded style
        - save stylized image
        """
        pk = self.pk

        self.img_format = str(self.styled_image).split(".")[-1]
        super().save(*args, **kwargs)

        if not settings.TESTING:
            # If pk is None means posting of new image,use AI for style image
            # If pk is not None means editing already existed image, dont use AI for style image
            if pk == None:
                original_img_path = self.original_image.uploaded_image.path
                style_img_path = self.styled_image.path

                styled_image = Transfer_Style_Image().stylizing_image(
                    original_img_path, style_img_path
                )
                styled_image.save(self.styled_image.path)

class DemoStyler(models.Model):
    original_image = models.ImageField(blank=False, null=False, upload_to="demo/")
    style_image = models.ImageField(blank=False, null=False, upload_to="demo/")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Resize demo images to max
        height, width, resized_img = Resize_image.resizing(
            self.original_image, 400,400
        )
        height, width, resized_style_img = Resize_image.resizing(
            self.style_image, 400,400
        )

        resized_img.save(self.original_image.path)
        resized_style_img.save(self.style_image.path)

        original_img_path = self.original_image.path
        style_img_path = self.style_image.path

        styled_image = Transfer_Style_Image().stylizing_image(
            original_img_path, style_img_path
        )
        styled_image.save(self.style_image.path)

