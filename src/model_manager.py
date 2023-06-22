from keras_retinanet import models
import pandas as pd
import numpy as np
from src.OCR import OCR


def load_model(message):
    if message['DOC_TYPE'] == 'RG':
        return models.load_model('./models/modelo_RG.h5', backbone_name='resnet50')

    elif message['DOC_TYPE'] == 'CNH':
        return models.load_model('./models/modelo_CNH.h5', backbone_name='resnet50')

    elif message['DOC_TYPE'] == 'CPF':
        return models.load_model('./models/modelo_CPF.h5', backbone_name='resnet50')

    #elif message['DOC_TYPE'] == 'RNE':
    #    return models.load_model('./models/modelo_CNH.h5', backbone_name='resnet50')
    #
    #elif message['DOC_TYPE'] == 'PASSAPORTE':
    #    return models.load_model('./models/modelo_CNH.h5', backbone_name='resnet50')
    #
    #elif message['DOC_TYPE'] == 'DIPLOMA_CERTIDAO':
    #    return models.load_model('./models/modelo_CNH.h5', backbone_name='resnet50')

    else:
        raise ValueError("Invalid Document Type Provided on Message")


def extract_data_from_prediction(message, dataframe):
    if dataframe['scores'].max() > 0.1:  #Deixei com 0.1 apenas para ter alguma detecção, o idela é 0.5
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

def process_RG_predicition(message, results, output_object):
    classes = ['RG_FRENTE', 'RG_VERSO', 'RG_NUMERO', 'RG_NOME', 'RG_NASCIMENTO', 'RG_CPF']
    results['labels'] = results.apply(lambda row: classes[int(row['labels'])],axis = 1)

    validar_documento = True

    RG_FRENTE     = verify_object_existence(results[results['labels'] == 'RG_FRENTE'])
    RG_VERSO      = verify_object_existence(results[results['labels'] == 'RG_VERSO'])
    RG_NASCIMENTO = verify_object_existence(results[results['labels'] == 'RG_NASCIMENTO'])

    RG_NOME   = extract_data_from_prediction(message, results[results['labels'] == 'RG_NOME'])
    RG_NUMERO = extract_data_from_prediction(message, results[results['labels'] == 'RG_NUMERO'])
    RG_CPF    =  extract_data_from_prediction(message, results[results['labels'] == 'RG_CPF'])

    if RG_NOME:
        output_object['VALIDAR_NOME'] = True
    else:
        output_object['VALIDAR_NOME'] = False
        valaildar_documento = False

    if RG_NUMERO == True and RG_CPF == True:
        output_object['VALIDAR_NUMERO'] = True
    else:
        output_object['VALIDAR_NUMERO'] = False
        valaildar_documento = False

    if RG_FRENTE == True and RG_VERSO == True:
        output_object['VALIDAR_FRENTE_VERSO'] = True
    else:
        output_object['VALIDAR_FRENTE_VERSO'] = False
        valaildar_documento = False

    if RG_NASCIMENTO:
        output_object['VALIDAR_DATA_NASCIMENTO'] = True
    else:
        output_object['VALIDAR_DATA_NASCIMENTO'] = False
        valaildar_documento = False

    output_object['VALIDAR_DOCUMENTO'] = validar_documento

    return output_object, {'RG_FRENTE':RG_FRENTE, 'RG_VERSO':RG_VERSO, 'RG_NASCIMENTO': RG_NASCIMENTO, 'RG_NOME':RG_NOME, 'RG_NUMERO': RG_NUMERO, 'RG_CPF': RG_CPF}


def process_CNH_predicition(message, results, output_object):
    classes = ['CNH_FRENTE', 'CNH_VERSO', 'CNH_NUMERO', 'CNH_NOME', 'RG_NUMERO', 'CPF_NUMERO']
    results['labels'] = results.apply(lambda row: classes[int(row['labels'])], axis=1)

    validar_documento = True

    CNH_FRENTE = verify_object_existence(results[results['labels'] == 'CNH_FRENTE'])
    CNH_VERSO = verify_object_existence(results[results['labels'] == 'CNH_VERSO'])

    CNH_NUMERO = extract_data_from_prediction(message, results[results['labels'] == 'CNH_NUMERO'])
    CNH_NOME = extract_data_from_prediction(message, results[results['labels'] == 'CNH_NOME'])
    RG_NUMERO = extract_data_from_prediction(message, results[results['labels'] == 'RG_NUMERO'])
    CPF_NUMERO = extract_data_from_prediction(message, results[results['labels'] == 'CPF_NUMERO'])

    if CNH_NOME:
        output_object['VALIDAR_NOME'] = True
    else:
        output_object['VALIDAR_NOME'] = False
        validar_documento = False

    if RG_NUMERO == True and CNH_NUMERO == True and CPF_NUMERO==True:
        output_object['VALIDAR_NUMERO'] = True
    else:
        output_object['VALIDAR_NUMERO'] = False
        validar_documento = False

    if CNH_FRENTE == True and CNH_VERSO == True:
        output_object['VALIDAR_FRENTE_VERSO'] = True
    else:
        output_object['VALIDAR_FRENTE_VERSO'] = False
        validar_documento = False

    #if CNH_NASCIMENTO:
    #    output_object['VALIDAR_DATA_NASCIMENTO'] = True
    #else:
    #    output_object['VALIDAR_DATA_NASCIMENTO'] = False
    #    validar_documento = False

    output_object['VALIDAR_DOCUMENTO'] = validar_documento

    return output_object, {'CNH_FRENTE':CNH_FRENTE, 'CNH_VERSO':CNH_VERSO, 'CNH_NUMERO': CNH_NUMERO, 'CNH_NOME':CNH_NOME, 'RG_NUMERO': RG_NUMERO, 'CPF_NUMERO': CPF_NUMERO}


def process_CPF_predicition(message, results, output_object):
    classes = ['CPF_FRENTE', 'CPF_NUMERO', 'CPF_NOME', 'CPF_ANTIGO_FRENTE', 'CPF_ANTIGO_NUMERO', 'CPF_ANTIGO_NOME']
    results['labels'] = results.apply(lambda row: classes[int(row['labels'])], axis=1)

    valaildar_documento = True

    CPF_FRENTE = verify_object_existence(results[results['labels'] == 'CPF_FRENTE'])
    CPF_NUMERO = extract_data_from_prediction(message, results[results['labels'] == 'CPF_NUMERO'])
    CPF_NOME = extract_data_from_prediction(message, results[results['labels'] == 'CPF_NOME'])

    CPF_ANTIGO_FRENTE = verify_object_existence(results[results['labels'] == 'CPF_ANTIGO_FRENTE'])
    CPF_ANTIGO_NUMERO = extract_data_from_prediction(message, results[results['labels'] == 'CPF_ANTIGO_NUMERO'])
    CPF_ANTIGO_NOME = extract_data_from_prediction(message, results[results['labels'] == 'CPF_ANTIGO_NOME'])

    if CPF_NOME==True or CPF_ANTIGO_NOME==True:
        output_object['VALIDAR_NOME'] = True
    else:
        output_object['VALIDAR_NOME'] = False
        valaildar_documento = False

    if CPF_NUMERO == True or CPF_ANTIGO_NUMERO == True:
        output_object['VALIDAR_NUMERO'] = True
    else:
        output_object['VALIDAR_NUMERO'] = False
        valaildar_documento = False

    if CPF_FRENTE == True or CPF_ANTIGO_FRENTE == True:
        output_object['VALIDAR_FRENTE_VERSO'] = True
    else:
        output_object['VALIDAR_FRENTE_VERSO'] = False
        valaildar_documento = False

    output_object['VALIDAR_DOCUMENTO'] = valaildar_documento

    return output_object, {'CPF_FRENTE':CPF_FRENTE, 'CPF_NUMERO':CPF_NUMERO, 'CPF_NOME': CPF_NOME, 'CPF_ANTIGO_FRENTE':CPF_ANTIGO_FRENTE, 'CPF_ANTIGO_NUMERO': CPF_ANTIGO_NUMERO, 'CPF_ANTIGO_NOME': CPF_ANTIGO_NOME}


#def process_RNE_predicition(message, results, output_object):
#    classes = ['RNE_NUMERO', 'RNE_NOME']
#    results['labels'] = results.apply(lambda row: classes[int(row['labels'])], axis=1)
#
#    valaildar_documento = True
#
#    RNE_NUMERO = extract_data_from_prediction(message, results[results['labels'] == 'RNE_NUMERO'])
#    RNE_NOME   = extract_data_from_prediction(message, results[results['labels'] == 'RNE_NOME'])
#
#
#    if RNE_NOME :
#        output_object['VALIDAR_NOME'] = True
#    else:
#        output_object['VALIDAR_NOME'] = False
#        valaildar_documento = False
#
#    if RNE_NUMERO:
#        output_object['VALIDAR_NUMERO'] = True
#    else:
#        output_object['VALIDAR_NUMERO'] = False
#        valaildar_documento = False
#
#    output_object['VALIDAR_DOCUMENTO'] = valaildar_documento
#
#    return output_object, {'RNE_NUMERO': RNE_NUMERO, 'RNE_NOME': RNE_NOME}


#def process_PASSAPORTE_predicition(message, results, output_object):
#    classes = ['RNE_NUMERO', 'RNE_NOME']
#    results['labels'] = results.apply(lambda row: classes[int(row['labels'])], axis=1)
#
#    valaildar_documento = True
#
#    PASSAPORTE_NOME = extract_data_from_prediction(message, results[results['labels'] == 'PASSAPORTE_NOME'])
#    PASSAPORTE_NUMERO = extract_data_from_prediction(message, results[results['labels'] == 'PASSAPORTE_NUMERO'])
#
#    if PASSAPORTE_NOME:
#        output_object['VALIDAR_NOME'] = True
#    else:
#        output_object['VALIDAR_NOME'] = False
#        valaildar_documento = False
#
#    if PASSAPORTE_NUMERO:
#        output_object['VALIDAR_NUMERO'] = True
#    else:
#        output_object['VALIDAR_NUMERO'] = False
#        valaildar_documento = False
#
#    output_object['VALIDAR_DOCUMENTO'] = valaildar_documento
#
#    return output_object, {'PASSAPORTE_NUMERO': PASSAPORTE_NUMERO, 'PASSAPORTE_NOME': PASSAPORTE_NOME}




# Esta função carece de maior elaboração por conta dos casos em que o texto pode sofrer quebra de linha
#def process_DIPLOMA_CERTIDAO_predicition(message, results, output_object):
#    classes = ['RNE_NUMERO', 'RNE_NOME']
#    results['labels'] = results.apply(lambda row: classes[int(row['labels'])], axis=1)
#
#    valaildar_documento = True
#
#    DIPLOMA_NOME          = extract_data_from_prediction(message, results[results['labels'] == 'DIPLOMA_NOME'])
#    DIPLOMA_GRAU          = extract_data_from_prediction(message, results[results['labels'] == 'DIPLOMA_GRAU'])
#    DIPLOMA_DATA_COLACAO  = extract_data_from_prediction(message, results[results['labels'] == 'DIPLOMA_DATA_COLACAO'])
#    CERTIDAO_NOME         = extract_data_from_prediction(message, results[results['labels'] == 'CERTIDAO_NOME'])
#    CERTIDAO_GRAU         = extract_data_from_prediction(message, results[results['labels'] == 'CERTIDAO_GRAU'])
#    CERTIDAO_DATA_COLACAO = extract_data_from_prediction(message, results[results['labels'] == 'CERTIDAO_DATA_COLACAO'])
#
#    if DIPLOMA_NOME:
#        output_object['VALIDAR_NOME'] = True
#    else:
#        output_object['VALIDAR_NOME'] = False
#        valaildar_documento = False
#
#    if DIPLOMA_GRAU:
#        output_object['VALIDAR_NUMERO'] = True
#    else:
#        output_object['VALIDAR_NUMERO'] = False
#        valaildar_documento = False
#
#    output_object['VALIDAR_DOCUMENTO'] = valaildar_documento
#
#    return output_object, {'PASSAPORTE_NUMERO': PASSAPORTE_NUMERO, 'PASSAPORTE_NOME': PASSAPORTE_NOME}


def process_prediction(message, boxes, scores, labels, output_object):
    results = pd.DataFrame(np.concatenate((labels.T,scores.T, boxes[0]), axis=1),columns=['labels','scores','xmin','ymin','xmax','ymax'])

    if message['DOC_TYPE'] == 'RG':
        return process_RG_predicition(message, results, output_object)

    elif message['DOC_TYPE'] == 'CNH':
        return process_CNH_predicition(message, results, output_object)

    elif message['DOC_TYPE'] == 'CPF':
        return process_CPF_predicition(message, results, output_object)

    #elif message['DOC_TYPE'] == 'RNE':
    #    return process_RNE_predicition(message, results, output_object)
    #
    #elif message['DOC_TYPE'] == 'PASSAPORTE':
    #    return process_PASSAPORTE_predicition(message, results, output_object)
    #
    #elif message['DOC_TYPE'] == 'DIPLOMA_CERTIDAO':
    #    return process_DIPLOMA_CERTIDAO_predicition(message, results, output_object)

    else:
        raise ValueError("Invalid Document Type Provided on Message")
