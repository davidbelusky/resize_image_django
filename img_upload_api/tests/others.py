import os
from PIL import Image
import io

def get_testing_media_path():
    current_path = os.path.abspath(os.getcwd()).replace('img_upload_api/tests', '')
    test_pic_folder = current_path + '/media/testing_pics'
    return test_pic_folder

def generate_image_file(name):
    """
    Create img for testing
    name: name of img 'test' = test.png
    return: created img
    """
    file = io.BytesIO()
    image = Image.new('RGBA', size=(150, 100), color=(155, 0, 0))
    image.save(file, 'png')
    file.name = f'{name}.png'
    file.seek(0)
    return file