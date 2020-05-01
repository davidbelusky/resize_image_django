from django.db import models
from django.conf import settings

from .others.resize_image import Resize_image


class Images(models.Model):
    img_name = models.CharField(max_length=25,blank=True)
    img_description = models.TextField(max_length=250,blank=True)
    img_format = models.CharField(max_length=5)
    favourite = models.BooleanField()
    #If testing run save tested pics to 'testing_pics/'
    if settings.TESTING:
        uploaded_image = models.ImageField(blank=False,null=False,upload_to='testing_pics/')
    #Normal run save pics to 'pics/'
    else:
        uploaded_image = models.ImageField(blank=False, null=False,upload_to='pics/')
    width = models.IntegerField(default=0)
    height = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        """
        - If name was not inpputed set default image name
        - Automatically get image format from img url
        - Resize image before upload to DB
        - Save original size of image to media/pics
        - Replace original img with resized img

        """

        # Get img format ex.(jpg,png...)
        self.img_format = str(self.uploaded_image).split('.')[-1]
        #If img_name = '' set default img file name
        #Exclude path before img name and format after img name ex.('/media/img1.jpg') to ('img1')
        if self.img_name == '':
            self.img_name = str(self.uploaded_image).replace('.'+ self.img_format,'')
        #Resize image and return resized height,width and resized image
        self.height, self.width, resized_img = Resize_image.resizing(self.uploaded_image, self.height, self.width)
        #Save original size of image
        super().save(*args, **kwargs)

        #Replace original img with resized img
        resized_img.save(self.uploaded_image.path)


