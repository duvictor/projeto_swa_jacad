from src.file_manager import read_image
from src.model_utils import load_model
import pandas as pd
from keras_retinanet.utils.image import preprocess_image
from craft_text_detector import Craft
import pytesseract
from pytesseract import Output
import numpy as np
import imutils
from utils import processa_str

import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"


# Paulo, vc precisa mudar esse path para o da maquina
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\Thiago\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

def crop_image(imagem, box=None, min_x=None, min_y=None, max_x=None, max_y=None):
    if box is not None and box.size > 0:
        # Presume que 'box' é uma array 2D onde cada linha é uma coordenada (x, y)
        min_x, min_y = np.min(box, axis=0)
        max_x, max_y = np.max(box, axis=0)
    elif min_x is None or min_y is None or max_x is None or max_y is None:
        raise ValueError("Coordenadas mínimas e máximas devem ser fornecidas se 'box' não for.")

    # Assegura que as coordenadas são inteiras, pois índices de array devem ser inteiros
    cropped_image = imagem[int(min_y):int(max_y), int(min_x):int(max_x)]

    return cropped_image

def craft_process(img_path):
    # Instancie o detector CRAFT
    craft = Craft(output_dir='output', crop_type="poly", cuda=False)

    # Caminho para a imagem de entrada
    image_path = img_path

    # Aplicar detecção de texto CRAFT na imagem
    prediction_result = craft.detect_text(image_path)

    # Os resultados incluem as coordenadas das regiões de texto detectadas
    text_regions = prediction_result['boxes']

    return text_regions

def rotate(img):
    results = pytesseract.image_to_osd(img, output_type=Output.DICT)
    rotated = imutils.rotate_bound(img, angle=results["rotate"])
    return rotated

def extract_text(img):
    return pytesseract.image_to_string(img,lang='por')

def circumscribe_bounding_boxes(bbox1, bbox2):
    """
    Calcula o bounding box que circunscreve dois bounding boxes dados.

    :param bbox1: Uma tupla (x_min, y_min, x_max, y_max) para o primeiro bounding box.
    :param bbox2: Uma tupla (x_min, y_min, x_max, y_max) para o segundo bounding box.
    :return: Uma tupla (x_min, y_min, x_max, y_max) para o bounding box circunscrito.
    """
    x_min = min(bbox1[0], bbox2[0])
    y_min = min(bbox1[1], bbox2[1])
    x_max = max(bbox1[2], bbox2[2])
    y_max = max(bbox1[3], bbox2[3])

    return (x_min, y_min, x_max, y_max)


def get_RG_frente_verso(message):
    model = load_model(message)

    img_to_retinanet, scale = read_image(message)
    boxes, scores, labels = model.predict_on_batch(img_to_retinanet)
    boxes /= scale

    results = pd.DataFrame(np.concatenate((labels.T,scores.T, boxes[0]), axis=1),columns=['labels','scores','xmin','ymin','xmax','ymax'])
    classes = ['RG_FRENTE', 'RG_VERSO', 'RG', 'NOME', 'DATA_NASCIMENTO', 'CPF']
    results['labels'] = results.apply(lambda row: classes[int(row['labels'])],axis = 1)

    frente = results[results['labels'] == 'RG_FRENTE']
    frente = frente[frente['scores' ] == frente['scores'].max()].drop_duplicates(subset='scores')

    verso = results[results['labels'] == 'RG_VERSO']
    verso = verso[verso['scores' ] == verso['scores'].max()].drop_duplicates(subset='scores')

    circumscribing_bbox = circumscribe_bounding_boxes(bbox1=[frente[['xmin']].values, frente[['ymin']].values, frente[['xmax']].values, frente[['ymax']].values],
        bbox2=[verso[['xmin']].values, verso[['ymin']].values, verso[['xmax']].values, verso[['ymax']].values])

    img_to_crop = np.array(message['IMAGE']).copy()
    if img_to_crop.shape[-1] == 4:
        # Convert RGBA to RGB
        img_to_crop = img_to_crop[..., :3]

    rg_img = crop_image(img_to_crop,box=None, min_x=circumscribing_bbox[0], min_y=circumscribing_bbox[1], max_x=circumscribing_bbox[2], max_y=circumscribing_bbox[3])

    rg_img_crop = rotate(rg_img)

    return rg_img_crop

def get_text(message):

    if message['DOC_TYPE'] == 'RG':
        rg_img_to_tesseract = get_RG_frente_verso(message)
        rg_text = pytesseract.image_to_string(rg_img_to_tesseract, lang='por')
        rg_text_all = processa_str(rg_text)
        return rg_text_all


    #if message['DOC_TYPE'] == 'RG':
    #    rg_img_to_craft = get_RG_frente_verso(message)
    #    rg_img_to_crop  = rg_img_to_craft.copy()   #craft mexe na imagem, então pra cortar precisa de uma cópia
    #    text_bboxes  = craft_process(rg_img_to_craft)
    #    rg_text = []
    #    for box in text_bboxes:
    #        crop = crop_image(rg_img_to_crop, box=box)
    #        rg_text.append(pytesseract.image_to_string(crop, lang='por'))
    #    rg_text_all = [processa_str(text) for text in rg_text]
    #    rg_text_concat = ' '.join(rg_text_all)
    #    return rg_text_concat
