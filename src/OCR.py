import keras_ocr
import cv2


pipeline = keras_ocr.pipeline.Pipeline()

def crop(imagem, b):
    x0 = int(b[0])
    y0 = int(b[1])
    width = int(b[2])
    height = int(b[3])
    return imagem[y0:height, x0:width, :]


def OCR(message, xmin,ymin,xmax,ymax):


    imagem_array = crop(message['IMAGE'], [xmin,ymin,xmax,ymax])
    image_keras_ocr = [cv2.cvtColor(imagem_array, cv2.COLOR_BGR2RGB)]

    prediction_groups = pipeline.recognize(image_keras_ocr)

    return prediction_groups[0][0][0]

