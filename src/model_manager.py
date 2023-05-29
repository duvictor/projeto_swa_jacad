from keras_retinanet import models
import pandas as pd
import numpy as np
from src.OCR import OCR

def load_model(message):
    if message['DOC_TYPE'] == 'RG':
        return models.load_model('./models/modelo_RG.h5', backbone_name='resnet50')

    elif message['DOC_TYPE'] == 'CNH':
        return models.load_model('./models/modelo_CNH.h5', backbone_name='resnet50')
    else:
        raise ValueError("Invalid Document Type Provided on Message")


def extract_data_from_prediction(message, dataframe):
    if dataframe['scores'].max() > 0.5:
        for i, row in dataframe[dataframe['scores'] == dataframe['scores'].max()].iterrows():
            if not dataframe['xmin'].empty:
                xmin, ymin, xmax, ymax = [row['xmin'], row['ymin'], row['xmax'], row['ymax']]
                DATA = OCR(message, xmin,ymin,xmax,ymax)
                return DATA
            else:
                return ''
    else:
        return ''

def verify_object_existence(dataframe):
    if dataframe['scores'].max() > 0.5:
        return True
    else:
        return False

def process_RG_predicition(message, results):
    classes = ['RG_FRENTE', 'RG_VERSO', 'RG_NUMERO', 'RG_NOME', 'RG_NASCIMENTO', 'RG_CPF']
    results['labels'] = results.apply(lambda row: classes[int(row['labels'])],axis = 1)

    RG_FRENTE     = verify_object_existence(results[results['labels'] == 'RG_FRENTE'])
    RG_VERSO      = verify_object_existence(results[results['labels'] == 'RG_VERSO'])
    RG_NASCIMENTO = verify_object_existence(results[results['labels'] == 'RG_NASCIMENTO'])

    RG_NOME   = extract_data_from_prediction(message, results[results['labels'] == 'RG_NOME'])
    RG_NUMERO = extract_data_from_prediction(message, results[results['labels'] == 'RG_NUMERO'])
    RG_CPF    =  extract_data_from_prediction(message, results[results['labels'] == 'RG_CPF'])

    return {'RG_FRENTE': RG_FRENTE, 'RG_VERSO': RG_VERSO, 'RG_NUMERO': RG_NUMERO, 'RG_NOME': RG_NOME, 'RG_NASCIMENTO': RG_NASCIMENTO, 'RG_CPF': RG_CPF}


def process_CNH_predicition(message, results):
    classes = ['CNH_FRENTE', 'CNH_VERSO', 'CNH_NUMERO', 'CNH_NOME', 'RG_NUMERO', 'CPF_NUMERO']
    results['labels'] = results.apply(lambda row: classes[int(row['labels'])], axis=1)

    CNH_FRENTE = verify_object_existence(results[results['labels'] == 'CNH_FRENTE'])
    CNH_VERSO = verify_object_existence(results[results['labels'] == 'CNH_VERSO'])

    CNH_NUMERO = extract_data_from_prediction(message, results[results['labels'] == 'CNH_NUMERO'])
    CNH_NOME = extract_data_from_prediction(message, results[results['labels'] == 'CNH_NOME'])
    RG_NUMERO = extract_data_from_prediction(message, results[results['labels'] == 'RG_NUMERO'])
    CPF_NUMERO = extract_data_from_prediction(message, results[results['labels'] == 'CPF_NUMERO'])

    return {'CNH_FRENTE':CNH_FRENTE, 'CNH_VERSO':CNH_VERSO, 'CNH_NUMERO': CNH_NUMERO, 'CNH_NOME':CNH_NOME, 'RG_NUMERO':RG_NUMERO, 'CPF_NUMERO': CPF_NUMERO}



def process_prediction(message, boxes, scores, labels):
    results = pd.DataFrame(np.concatenate((labels.T,scores.T, boxes[0]), axis=1),columns=['labels','scores','xmin','ymin','xmax','ymax'])

    if message['DOC_TYPE'] == 'RG':
        return process_RG_predicition(message, results)

    elif message['DOC_TYPE'] == 'CNH':
        return process_CNH_predicition(message, results)
    else:
        raise ValueError("Invalid Document Type Provided on Message")
