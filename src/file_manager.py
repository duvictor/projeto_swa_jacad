from PIL import Image
import numpy as np

from keras_retinanet.utils.image import preprocess_image, resize_image


def check_file_corruption(file_path):
    try:
        # Open the image file
        with Image.open(file_path) as image:
            # Check if the file can be loaded without errors
            image.verify()
    except (IOError, SyntaxError) as e:
        return True

    return False


def check_file_password(file_path):
    try:
        # Open the image file
        with Image.open(file_path) as image:
            # Check if the image has an "encrypted" mode
            if image.mode == "P":
                return True
            else:
                return False

    except (IOError, SyntaxError) as e:
        return False



def check_file_integrity(file_path):
    if check_file_corruption(file_path):
        return True

    elif check_file_password(file_path):
        return True

    else:
        return False

def read_image(message):

    image = np.array(message['IMAGE']).copy()
    if image.shape[-1] == 4:
        # Convert RGBA to RGB
        image = image[..., :3]
    image = preprocess_image(image)
    image, scale = resize_image(image)
    return np.expand_dims(image, axis=0), scale