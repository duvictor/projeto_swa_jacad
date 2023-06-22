import keras_ocr
import cv2


pipeline = keras_ocr.pipeline.Pipeline()

def crop(imagem, b):
    x0 = b[0]
    y0 = b[1]
    width = b[2]
    height = b[3]
    return imagem[y0:height, x0:width, :]


def OCR(message, xmin,ymin,xmax,ymax):

    imagem_array = None
    image_keras_ocr = [cv2.cvtColor(imagem_array, cv2.COLOR_BGR2RGB)]

    prediction_groups = pipeline.recognize(image_keras_ocr)


    return prediction_groups[0][0][0]