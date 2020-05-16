from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

#from .ai_models.image_style_transfer import Transfer_Style_Image
from .others.resize_image import Resize_image

#Paths for saving orig images,style images and styled images
def owner_directory_path(instance, filename):
    # Image upload to media/pics/owner_{owner_id}/
    return f'pics/owner_{instance.owner.id}/{filename}'

def owner_directory_path_styles(instance, filename):
    # Styled image upload to media/pics/owner_{owner_id}/styles/
    return f'pics/owner_{instance.owner.id}/styled_images/{filename}'

class Images(models.Model):
    img_name = models.CharField(max_length=25,blank=False,null=False)
    img_description = models.TextField(max_length=250,blank=True)
    img_format = models.CharField(max_length=5) #ex.(jpg,png)

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
        #ex. "owner: david, img_name: first_image"
        return f'owner: {self.owner}, img_name: {self.img_name}'

    def save(self, *args, **kwargs):
        """
        - Automatically get image format from img path
        - Resize image before upload to DB
        - Save original size of image to media/pics
        - Replace original image with resized image
        """
        # Get img format ex.(jpg,png...)
        self.img_format = str(self.uploaded_image).split('.')[-1]
        #Resize image and return resized height,width and resized image
        self.height, self.width, resized_img = Resize_image.resizing(self.uploaded_image, self.height, self.width)
        #Save original size of image
        super().save(*args, **kwargs)
        #Replace original img with resized img
        resized_img.save(self.uploaded_image.path)

class StyleImage(models.Model):
    img_name = models.CharField(max_length=25,blank=False,null=False)
    if settings.TESTING:
        styled_image = models.ImageField(blank=False, null=False, upload_to='testing_pics/styled_images')
    else:
        styled_image = models.ImageField(blank=False,null=False,upload_to=owner_directory_path_styles)
    img_description = models.TextField(max_length=250,blank=True)
    img_format = models.CharField(max_length=5) #ex.(jpg,png)

    created_date = models.DateTimeField(auto_now_add=True)
    original_image = models.ForeignKey(Images,null=True ,on_delete=models.SET_NULL)
    favourite = models.BooleanField(default=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    share_user = models.ManyToManyField(User,related_name='shared_user_styled',blank=True,null=True)

    def __str__(self):
        #ex. "owner: david, img_name: first_image"
        return f'owner: {self.owner}, img_name: {self.img_name}'

    def save(self, *args, **kwargs):
        """
        - stylize original image with uploaded style
        - save stylized image
        """
        self.img_format = str(self.styled_image).split('.')[-1]
        super().save(*args, **kwargs)

        original_img_path = self.original_image.uploaded_image.path
        style_img_path = self.styled_image.path

       #styled_image = Transfer_Style_Image().stylizing_image(original_img_path, style_img_path)
        #styled_image.save(self.styled_image.path)



