from PIL import Image


class Resize_image():
    @staticmethod
    def resizing(original_img,height,width):
        """
        original_img = uploaded image by user with original sizes
        height = user input height to resize
        width = user input width to resize

        If width or height = 0 then set original parameter of size
        Max allowed width and height = 1920x1080 (if input is higher than max allowed automatically set to max allowed size)

        return: corrected height,width and resized image
        """

        img = Image.open(original_img)
        img_width,img_height = img.size
        #If width or height was not inputted set original width or height of img
        if width == 0:
            width = img_width
        if height == 0:
            height = img_height

        #If width > 1920 then set to max allowed width. If height > 1080 then automatically set to max allowed height
        if width > 1920: width = 1920
        if height > 1080: height= 1080
        #Set output size
        output_size = (width, height)

        #apply resize to IMG
        img_resized = img.resize(output_size,Image.ANTIALIAS)
        #Return resized height,width and resized img
        return height,width,img_resized


