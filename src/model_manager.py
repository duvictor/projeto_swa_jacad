from keras_retinanet import models
import pandas as pd
import numpy as np
from src.OCR import OCR
from utils import calcular_intervalo_um_ano, processa_str, verificar_data_compra
import datetime


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
    elif message['DOC_TYPE'] == 'DIPLOMA':
        return models.load_model('./models/modelo_Diploma.h5', backbone_name='resnet50')

    elif message['DOC_TYPE'] == 'CERTIFICADO':
        return models.load_model('./models/modelo_Certidao.h5', backbone_name='resnet50')

    else:
        raise ValueError("Invalid Document Type Provided on Message")


def extract_data_from_prediction(message, dataframe):
    if dataframe['scores'].max() > 0.1:  #Deixei com 0.1 apenas para ter alguma detecção, o ideal é 0.5
        for i, row in dataframe[dataframe['scores'] == dataframe['scores'].max()].iterrows():
            if not dataframe['xmin'].empty:
                try:
                    xmin, ymin, xmax, ymax = [row['xmin'], row['ymin'], row['xmax'], row['ymax']]
                    DATA = processa_str(OCR(message, xmin,ymin,xmax,ymax))
                    return DATA
                except:
                    return ''
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
    RG_CPF    = extract_data_from_prediction(message, results[results['labels'] == 'RG_CPF'])

    if RG_NOME == message['DOC_NUMBER']['RG_NOME']:
        output_object['VALIDAR_NOME'] = True
    else:
        output_object['VALIDAR_NOME'] = False
        validar_documento = False

    if RG_FRENTE == True and RG_VERSO == True:
        output_object['VALIDAR_FRENTE_VERSO'] = True
    else:
        output_object['VALIDAR_FRENTE_VERSO'] = False
        validar_documento = False

    if RG_NASCIMENTO:
        output_object['VALIDAR_DATA_NASCIMENTO'] = True
    else:
        output_object['VALIDAR_DATA_NASCIMENTO'] = False
        validar_documento = False

    if message['DOC_NUMBER']['RG_CPF'] != '':
        if RG_NUMERO == message['DOC_NUMBER']['RG_NUMERO'] and RG_CPF == message['DOC_NUMBER']['RG_CPF']:
            output_object['VALIDAR_NUMERO'] = True
        else:
            output_object['VALIDAR_NUMERO'] = False
            validar_documento = False
    else:
        RG_CPF = 'Número de CPF não informado no RG.'
        if RG_NUMERO == message['DOC_NUMBER']['RG_NUMERO']:
            output_object['VALIDAR_NUMERO'] = True
        else:
            output_object['VALIDAR_NUMERO'] = False
            validar_documento = False

    output_object['VALIDAR_DOCUMENTO'] = validar_documento

    return output_object, {'RG_FRENTE':RG_FRENTE, 'RG_VERSO':RG_VERSO, 'RG_NASCIMENTO': RG_NASCIMENTO, 'RG_NOME':RG_NOME, 'RG_NUMERO': RG_NUMERO, 'RG_CPF': RG_CPF}


def process_CNH_predicition(message, results, output_object):
    classes = ['CNH_FRENTE', 'CNH_VERSO', 'CNH_NUMERO', 'CNH_NOME', 'RG_NUMERO', 'CPF_NUMERO', 'CNH_NASCIMENTO']
    results['labels'] = results.apply(lambda row: classes[int(row['labels'])], axis=1)

    validar_documento = True

    CNH_FRENTE     = verify_object_existence(results[results['labels'] == 'CNH_FRENTE'])
    CNH_VERSO      = verify_object_existence(results[results['labels'] == 'CNH_VERSO'])
    CNH_NASCIMENTO = verify_object_existence(results[results['labels'] == 'CNH_NASCIMENTO'])

    CNH_NUMERO = extract_data_from_prediction(message, results[results['labels'] == 'CNH_NUMERO'])
    CNH_NOME   = extract_data_from_prediction(message, results[results['labels'] == 'CNH_NOME'])
    RG_NUMERO  = extract_data_from_prediction(message, results[results['labels'] == 'RG_NUMERO'])
    CPF_NUMERO = extract_data_from_prediction(message, results[results['labels'] == 'CPF_NUMERO'])



    if CNH_NOME == message['DOC_NUMBER']['CNH_NOME']:
        output_object['VALIDAR_NOME'] = True
    else:
        output_object['VALIDAR_NOME'] = False
        validar_documento = False

    if CNH_FRENTE == True and CNH_VERSO == True:
        output_object['VALIDAR_FRENTE_VERSO'] = True
    else:
        output_object['VALIDAR_FRENTE_VERSO'] = False
        validar_documento = False

    if CNH_NASCIMENTO:
       output_object['VALIDAR_DATA_NASCIMENTO'] = True
    else:
        output_object['VALIDAR_DATA_NASCIMENTO'] = False
        validar_documento = False


    if message['DOC_NUMBER']['RG_NUMERO'] != '':
        if message['DOC_NUMBER']['CPF_NUMERO'] != '':
            if RG_NUMERO == message['DOC_NUMBER']['RG_NUMERO'] and CNH_NUMERO == message['DOC_NUMBER']['CNH_NUMERO'] and CPF_NUMERO == message['DOC_NUMBER']['CPF_NUMERO']:
                output_object['VALIDAR_NUMERO'] = True
            else:
                output_object['VALIDAR_NUMERO'] = False
                validar_documento = False
        else:
            CPF_NUMERO = 'Número de CPF não informado na CNH.'
            if RG_NUMERO == message['DOC_NUMBER']['RG_NUMERO'] and CNH_NUMERO == message['DOC_NUMBER']['CNH_NUMERO']:
                output_object['VALIDAR_NUMERO'] = True
            else:
                output_object['VALIDAR_NUMERO'] = False
                validar_documento = False
    else:
        RG_NUMERO = 'Número de CPF não informado na CNH.'
        if message['DOC_NUMBER']['CPF_NUMERO'] != '':
            if CNH_NUMERO == message['DOC_NUMBER']['CNH_NUMERO'] and CPF_NUMERO == message['DOC_NUMBER']['CPF_NUMERO']:
                output_object['VALIDAR_NUMERO'] = True
            else:
                output_object['VALIDAR_NUMERO'] = False
                validar_documento = False
        else:
            RG_NUMERO = 'Número de CPF não informado na CNH.'
            CPF_NUMERO = 'Número de CPF não informado na CNH.'
            if CNH_NUMERO == message['DOC_NUMBER']['CNH_NUMERO']:
                output_object['VALIDAR_NUMERO'] = True
            else:
                output_object['VALIDAR_NUMERO'] = False
                validar_documento = False

    output_object['VALIDAR_DOCUMENTO'] = validar_documento

    return output_object, {'CNH_FRENTE':CNH_FRENTE, 'CNH_VERSO':CNH_VERSO, 'CNH_NUMERO': CNH_NUMERO, 'CNH_NOME':CNH_NOME, 'RG_NUMERO': RG_NUMERO, 'CPF_NUMERO': CPF_NUMERO, 'CNH_NASCIMENTO': CNH_NASCIMENTO}


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

    if CPF_NOME==message['DOC_NUMBER']['CPF_NOME'] or CPF_ANTIGO_NOME==message['DOC_NUMBER']['CPF_NOME']:
        output_object['VALIDAR_NOME'] = True
    else:
        output_object['VALIDAR_NOME'] = False
        valaildar_documento = False

    if CPF_NUMERO == message['DOC_NUMBER']['CPF_NUMERO'] or CPF_ANTIGO_NUMERO == message['DOC_NUMBER']['CPF_NUMERO']:
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



def process_DIPLOMA_predicition(message, results, output_object):
    classes = ['DOC_DIPLOMA', 'DOC_NOME', 'DOC_DATA_COLACAO', 'DOC_GRAU']
    results['labels'] = results.apply(lambda row: classes[int(row['labels'])], axis=1)

    validar_documento = True

    DOC_DIPLOMA      = verify_object_existence(results[results['labels'] == 'DOC_DIPLOMA'])
    DOC_DATA_COLACAO = extract_data_from_prediction(message, results[results['labels'] == 'DOC_DATA_COLACAO'])
    DOC_NOME         = extract_data_from_prediction(message, results[results['labels'] == 'DOC_NOME'])
    DOC_GRAU         = extract_data_from_prediction(message, results[results['labels'] == 'DOC_GRAU'])

    if not DOC_DIPLOMA:
        output_object['VALIDAR_FRENTE_VERSO'] = True
    else:
        output_object['VALIDAR_FRENTE_VERSO'] = False
        validar_documento = False

    if DOC_NOME==message['DOC_NUMBER']['DOC_NOME']:
        output_object['VALIDAR_DIPLOMA_NOME'] = True
    else:
        output_object['VALIDAR_DIPLOMA_NOME'] = False
        validar_documento = False

    grau = ['bacharel', 'bacharelado', 'bacharela', 'licenciatura', 'licenciado', 'licenciada', 'tecnólogo',
            'tecnóloga', 'curso superior de tecnologia']
    if DOC_GRAU == message['DOC_NUMBER']['DOC_GRAU']:
        if 'sequencial' in DOC_GRAU or 'formacao especifica' in DOC_GRAU:
            output_object['VALIDAR_DIPLOMA_GRAU'] = False
            validar_documento = False

        if DOC_GRAU in grau:
            output_object['VALIDAR_RESTRICOES_GRAU'] = True
    else:
        output_object['VALIDAR_DIPLOMA_GRAU'] = False
        validar_documento = False

    if DOC_DATA_COLACAO == message['DOC_NUMBER']['DOC_DATA_COLACAO']:
        output_object['VALIDAR_DIPLOMA_COLACAO'] = True
        output_object['VALIDAR_DATA_COMPRA']     = verificar_data_compra(message['DOC_NUMBER']['DATA_COMPRA'], DOC_DATA_COLACAO)
    else:
        output_object['VALIDAR_DIPLOMA_COLACAO'] = False
        validar_documento = False

    output_object['VALIDAR_DOCUMENTO'] = validar_documento

    return output_object, {'DOC_DIPLOMA':DOC_DIPLOMA, 'DOC_NOME':DOC_NOME, 'DOC_GRAU': DOC_GRAU, 'DOC_DATA_COLACAO':DOC_DATA_COLACAO}

def process_CERTI_predicition(message, results, output_object):
    classes = ['DOC_CERTIFICADO', 'DOC_NOME', 'DOC_DATA_EMISSAO', 'DOC_GRAU', 'DOC_DATA_COLACAO']
    results['labels'] = results.apply(lambda row: classes[int(row['labels'])], axis=1)

    validar_documento = True

    DOC_CERTIFICADO       = verify_object_existence(results[results['labels'] == 'DOC_CERTIFICADO'])
    CERTIDAO_NOME         = extract_data_from_prediction(message, results[results['labels'] == 'DOC_NOME'])
    CERTIDAO_GRAU         = extract_data_from_prediction(message, results[results['labels'] == 'DOC_GRAU'])
    CERTIDAO_DATA_COLACAO = extract_data_from_prediction(message, results[results['labels'] == 'DOC_DATA_COLACAO'])
    CERTIDAO_DATA_EMISSAO = extract_data_from_prediction(message, results[results['labels'] == 'DOC_DATA_EMISSAO'])

    if not DOC_CERTIFICADO:
        output_object['VALIDAR_FRENTE_VERSO'] = True
    else:
        output_object['VALIDAR_FRENTE_VERSO'] = False
        validar_documento = False

    if CERTIDAO_NOME == message['DOC_NUMBER']['DOC_NOME']:
        output_object['VALIDAR_CERTIDAO_NOME'] = True
    else:
        output_object['VALIDAR_CERTIDAO_NOME'] = False
        validar_documento = False

    grau = ['bacharel', 'bacharelado', 'bacharela', 'licenciatura', 'licenciado', 'licenciada', 'tecnólogo', 'tecnóloga', 'curso superior de tecnologia']
    if CERTIDAO_GRAU == message['DOC_NUMBER']['DOC_GRAU']:
        if 'sequencial' in CERTIDAO_GRAU or 'formacao especifica' in CERTIDAO_GRAU:
            output_object['VALIDAR_RESTRICOES_GRAU_SFE'] = False
            validar_documento = False

        else:
            output_object['VALIDAR_RESTRICOES_GRAU_SFE'] = True

        if CERTIDAO_GRAU in grau:
            output_object['VALIDAR_RESTRICOES_GRAU_BLT'] = True

        else:
            output_object['VALIDAR_RESTRICOES_GRAU_BLT'] = False
            validar_documento = False

    else:
        output_object['VALIDAR_CERTIDAO_GRAU'] = False
        validar_documento = False

    if CERTIDAO_DATA_COLACAO == message['DOC_NUMBER']['DOC_DATA_COLACAO']:
        output_object['VALIDAR_CERTIDAO_COLACAO'] = True
        output_object['VALIDAR_DATA_COMPRA'] = verificar_data_compra(message['DOC_NUMBER']['DATA_COMPRA'], CERTIDAO_DATA_COLACAO)
    else:
        output_object['VALIDAR_CERTIDAO_COLACAO'] = False
        validar_documento = False

    if CERTIDAO_DATA_EMISSAO == message['DOC_NUMBER']['DOC_DATA_EMISSAO']:
        output_object['VALIDAR_CERTIDAO_EMISSAO'] = True
    else:
        output_object['VALIDAR_CERTIDAO_EMISSAO'] = False
        validar_documento = False

    if output_object['VALIDAR_CERTIDAO_EMISSAO'] == True and output_object['VALIDAR_CERTIDAO_COLACAO'] == True:
        if calcular_intervalo_um_ano(CERTIDAO_DATA_COLACAO, CERTIDAO_DATA_EMISSAO):
            validar_documento = False
            output_object['VALIDAR_RESTRICAO_DATA_EMISSAO_COLACAO'] = False
        if calcular_intervalo_um_ano(CERTIDAO_DATA_EMISSAO, datetime.now().date().strftime('%d/%m/%Y')):
            validar_documento = False
            output_object['VALIDAR_RESTRICAO_DATA_EMISSAO_HOJE'] = False


    if validar_documento == True:
        output_object['VALIDAR_DOCUMENTO'] = 'ACEITE PROVISORIO'

    return output_object, {'DOC_NOME': CERTIDAO_NOME, 'DOC_GRAU': CERTIDAO_GRAU, 'DOC_DATA_COLACAO': CERTIDAO_DATA_COLACAO, 'DOC_DATA_EMISSAO': CERTIDAO_DATA_EMISSAO}


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
    elif message['DOC_TYPE'] == 'DIPLOMA':
        return process_DIPLOMA_predicition(message, results, output_object)

    elif message['DOC_TYPE'] == 'CERTIFICADO':
        return process_CERTI_predicition(message, results, output_object)
    else:
        raise ValueError("Invalid Document Type Provided on Message")
