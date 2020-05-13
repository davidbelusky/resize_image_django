import tensorflow as tf
import tensorflow_hub as hub

import numpy as np
import PIL.Image
import os

class Transfer_Style_Image():
  def __init__(self):
    #set directory for saving model (default tensorflow directory cannot be accessed)
    os.environ['TFHUB_CACHE_DIR'] = '/home/user/workspace/tf_cache'

  def stylizing_image(self,content_path,style_path):
    """
    - Load content image and style image
    - Load hub model for stylizing images
    - apply hub model to images

    :return stylized image
    """
    #Load images
    content_image = self.load_img(content_path)
    style_image = self.load_img(style_path)
    #Load hub_module for image stylizing
    hub_module = hub.load('https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/2')
    #Apply stylizing module
    stylized_image = hub_module(tf.constant(content_image), tf.constant(style_image))[0]
    #Convert tensor to image array
    img = self.tensor_to_image(stylized_image)
    return img

  def tensor_to_image(self,tensor):
    """
    - convert tensor to 8bit (multiply by 255)
    - convert tensor to numpy array
    - numpy array must be 3 dim. (matrix)
    :return image array
    """
    #convert tensor to 8bit
    tensor = tensor*255
    #convert tensor to numpy
    tensor = np.array(tensor, dtype=np.uint8)
    #check if numpy array is 3 dimension (matrix)
    if np.ndim(tensor)>3:
      assert tensor.shape[0] == 1
      tensor = tensor[0]
    #return arrayed img
    return PIL.Image.fromarray(tensor)

  def load_img(self,path_to_img):
    """
    Load and resize images
    - max allowed dimensions = 512  (restricted for faster converting)
    """
    max_dim = 512
    img = tf.io.read_file(path_to_img)
    #Convert img to matrix
    img = tf.image.decode_image(img, channels=3)
    #Convert matrix from uint8 to float32
    img = tf.image.convert_image_dtype(img, tf.float32)
    #convert matrix to vector
    shape = tf.cast(tf.shape(img)[:-1], tf.float32)
    #get highest dimension in img
    long_dim = max(shape)
    #calculate scale based on max allowed dim
    scale = max_dim / long_dim
    #reshape img to max allowed dim
    new_shape = tf.cast(shape * scale, tf.int32)
    #resize img
    img = tf.image.resize(img, new_shape)
    img = img[tf.newaxis, :]
    return img
