from PIL import Image
import io

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