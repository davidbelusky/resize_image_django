import os

def get_testing_media_path():
    current_path = os.path.abspath(os.getcwd()).replace('img_upload_api/tests', '')
    test_pic_folder = current_path + '/media/testing_pics'
    return test_pic_folder