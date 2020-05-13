from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

from .ml_models.image_style_transfer import Transfer_Style_Image
from .others.resize_image import Resize_image

#Paths for saving orig images,style images and styled images
def owner_directory_path(instance, filename):
    # Image upload to media/pics/owner_{owner_id}/
    return f'pics/owner_{instance.owner.id}/{filename}'

def owner_directory_path_styles(instance, filename):
    # Image upload to media/pics/owner_{owner_id}/styles/
    return f'pics/owner_{instance.owner.id}/styled_images/{filename}'


class Images(models.Model):
    img_name = models.CharField(max_length=25,blank=True,unique=True)
    img_description = models.TextField(max_length=250,blank=True)
    img_format = models.CharField(max_length=5)
    created_date = models.DateTimeField(auto_now_add=True)
    favourite = models.BooleanField(default=False)
    #If testing run save tested pics to 'testing_pics/'
    if settings.TESTING:
        uploaded_image = models.ImageField(blank=False,null=False,upload_to='testing_pics/')
    #Normal run save pics to 'pics/'
    else:
        uploaded_image = models.ImageField(blank=False, null=False,upload_to=owner_directory_path)
    width = models.IntegerField(default=0)
    height = models.IntegerField(default=0)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    share_user = models.ManyToManyField(User,related_name='shared_user',blank=True,null=True)

    def __str__(self):
        return f'owner: {self.owner}, img_name: {self.img_name}'

    def save(self, *args, **kwargs):
        """
        - If name was not inpputed set default image name
        - If length of name is > 25 characters then set it to first 25 chars
        - Automatically get image format from img path
        - Resize image before upload to DB
        - Save original size of image to media/pics
        - Replace original image with resized image
        """
        # Get img format ex.(jpg,png...)
        self.img_format = str(self.uploaded_image).split('.')[-1]
        #If img_name = '' set default img file name
        #Exclude path before img name and format after img name ex.('/media/img1.jpg') to ('img1')
        if self.img_name == '':
            self.img_name = str(self.uploaded_image).replace('.'+ self.img_format,'')
        #Max allowed len of name is 25, if img_name is longer then automatically short name to first 25 letters
        if len(self.img_name) > 25:
            self.img_name = self.img_name[:25]
        #Resize image and return resized height,width and resized image
        self.height, self.width, resized_img = Resize_image.resizing(self.uploaded_image, self.height, self.width)
        #Save original size of image
        super().save(*args, **kwargs)

        #Replace original img with resized img
        resized_img.save(self.uploaded_image.path)

class StyleImage(models.Model):
    styled_img_name = models.CharField(max_length=25,blank=False,unique=True)
    styled_image = models.ImageField(blank=False,null=False,upload_to=owner_directory_path_styles)
    original_image = models.ForeignKey(Images, on_delete=models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        """
        Stylize original image with uploaded style and save styled imaged to DB
        """
        super().save(*args, **kwargs)

        original_img_path = self.original_image.uploaded_image.path
        style_img_path = self.styled_image.path

        styled_image = Transfer_Style_Image().stylizing_image(original_img_path, style_img_path)
        styled_image.save(self.styled_image.path)



