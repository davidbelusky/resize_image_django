from django.db import models
from django.conf import settings


from .others.resize_image import Resize_image

class Images(models.Model):
    #If testing run save tested pics to 'testing_pics/'
    if settings.TESTING:
        uploaded_image = models.ImageField(blank=False,null=False,upload_to='testing_pics/')
    #Normal run save pics to 'pics/'
    else:
        uploaded_image = models.ImageField(blank=False, null=False, upload_to='pics/')#,height_field='height',width_field='width')
    width = models.IntegerField(default=0)
    height = models.IntegerField(default=0)


    def save(self, *args, **kwargs):
        """
        - Resize image before upload to DB
        - Save original size of image to media/pics
        - Replace original img with resized img

        """
        #Resize image and return resized height,width and resized image
        self.height, self.width, resized_img = Resize_image.resizing(self.uploaded_image, self.height, self.width)
        #Save original size of image
        super().save(*args, **kwargs)
        #Replace original img with resized img
        resized_img.save(self.uploaded_image.path)


