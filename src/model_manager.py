
import pandas as pd
import numpy as np
import datetime
from src.cnh_manager import process_prediction_cnh_cpf, process_prediction_cnh_rg, process_prediction_cnh_numero, process_prediction_cnh_nome
from src.upload_s3 import publicar_json
from src.persistencia import inserir_resultado_ia
import uuid
from src.RG_utils import get_text
from src.model_utils import verify_object_existence, extract_data_from_prediction
from utils import verificar_data_compra, calcular_intervalo_um_ano

#usado para verificar a similaridade de strings, solução paleativa até que o ocr esteja 100%
from difflib import SequenceMatcher


def process_RG_predicition(message, results, output_object):
    classes = ['RG_FRENTE', 'RG_VERSO', 'RG', 'NOME', 'DATA_NASCIMENTO', 'CPF']
    results['labels'] = results.apply(lambda row: classes[int(row['labels'])],axis = 1)

    validar_documento = True

    RG_FRENTE     = verify_object_existence(results[results['labels'] == 'RG_FRENTE'])
    RG_VERSO      = verify_object_existence(results[results['labels'] == 'RG_VERSO'])
    #DATA_NASCIMENTO = verify_object_existence(results[results['labels'] == 'RG_NASCIMENTO'])

    output_object['VALIDAR_CPF']             = False
    output_object['VALIDAR_RG']              = False
    output_object['VALIDAR_DATA_NASCIMENTO'] = False
    output_object['VALIDAR_NOME']            = False


    if RG_FRENTE == True and RG_VERSO == True:
        #NOME   = extract_data_from_prediction(message, results[results['labels'] == 'NOME'])
        #RG = extract_data_from_prediction(message, results[results['labels'] == 'RG'])
        #CPF    = extract_data_from_prediction(message, results[results['labels'] == 'CPF'])

        output_object['VALIDAR_FRENTE_VERSO'] = True


        texto = get_text(message)
        texto_numero = texto.replace(' ', '')

        if message['DOC_NUMBER']['NOME'] in texto:
            output_object['VALIDAR_NOME'] = True
        else:
            validar_documento = False

        if message['DOC_NUMBER']['DATA_NASCIMENTO'] in texto:
            output_object['VALIDAR_DATA_NASCIMENTO'] = True
        else:
            validar_documento = False

        if message['DOC_NUMBER']['CPF'] != '':
            if message['DOC_NUMBER']['CPF'] in texto:
                output_object['VALIDAR_CPF'] = True
            elif message['DOC_NUMBER']['CPF'] in texto_numero:
                output_object['VALIDAR_CPF'] = True
            else:
                validar_documento = False

        if message['DOC_NUMBER']['RG'] in texto:
            output_object['VALIDAR_RG'] = True
        elif message['DOC_NUMBER']['RG'] in texto_numero:
            output_object['VALIDAR_RG'] = True
        else:
            validar_documento = False

        output_object['VALIDAR_DOCUMENTO'] = validar_documento

    else:
        output_object['VALIDAR_FRENTE_VERSO'] = False
        output_object['VALIDAR_DOCUMENTO'] = False

    return output_object, {'RG_FRENTE':RG_FRENTE, 'RG_VERSO':RG_VERSO, 'RG': output_object['VALIDAR_RG'],  'DATA_NASCIMENTO': output_object['VALIDAR_DATA_NASCIMENTO'], 'NOME': output_object['VALIDAR_NOME'], 'CPF': output_object['VALIDAR_CPF']}

def process_CNH_predicition(message, results, output_object):
    classes = ['CNH_FRENTE', 'CNH_VERSO', 'CNH', 'NOME', 'RG', 'CPF', 'DATA_NASCIMENTO']
    results['labels'] = results.apply(lambda row: classes[int(row['labels'])], axis=1)

    validar_documento = True

    # CNH_FRENTE     = verify_object_existence(results[results['labels'] == 'CNH_FRENTE'])
    # CNH_VERSO      = verify_object_existence(results[results['labels'] == 'CNH_VERSO'])
    # CNH_NASCIMENTO = verify_object_existence(results[results['labels'] == 'CNH_NASCIMENTO'])
    # COMENTADO, POIS ESTAMOS USANDO CNH FIXA, MODELO PDF TIRADO DO APP
    CNH_FRENTE = True
    CNH_VERSO = True
    DATA_NASCIMENTO = True

    CNH, cropped_cnh = process_prediction_cnh_numero(message)
    NOME, cropped_nome = process_prediction_cnh_nome(message)
    RG, cropped_rg = process_prediction_cnh_rg(message)
    CPF, cropped_cpf = process_prediction_cnh_cpf(message)

    message['cropped_cnh'] = cropped_cnh.tostring()
    message['cropped_nome'] = cropped_nome.tostring()
    message['cropped_rg'] = cropped_rg.tostring()
    message['cropped_cpf'] = cropped_cpf.tostring()

    message['predict_cnh'] = CNH
    message['predict_nome'] = NOME
    message['predict_rg'] = RG
    message['predict_cpf'] = CPF

    uuid_s3 = str(uuid.uuid4())

    # criando json com crop e valores corretos e enviando os crops com os valores corretos para s3
    publicar_json(message, uuid_s3)


    metrica_nome = SequenceMatcher(None, NOME, message['DOC_NUMBER']['NOME']).ratio()

    # gravando no banco relacional a predição do nome da cnh
    inserir_resultado_ia(message['DOC_TYPE'], message['DOC_NUMBER']['NOME'], NOME, 'NOME', message['FILE'], uuid_s3, metrica_nome)

    if metrica_nome >= 0.30:
        output_object['VALIDAR_NOME'] = True
    else:
        output_object['VALIDAR_NOME'] = False
        validar_documento = False

    if CNH_FRENTE == True and CNH_VERSO == True:
        output_object['VALIDAR_FRENTE_VERSO'] = True
    else:
        output_object['VALIDAR_FRENTE_VERSO'] = False
        validar_documento = False

    if DATA_NASCIMENTO:
       output_object['VALIDAR_DATA_NASCIMENTO'] = True
    else:
        output_object['VALIDAR_DATA_NASCIMENTO'] = False
        validar_documento = False

    metrica_cpf = SequenceMatcher(None, CPF, message['DOC_NUMBER']['CPF']).ratio()
    inserir_resultado_ia(message['DOC_TYPE'], message['DOC_NUMBER']['CPF'], CPF, 'CPF', message['FILE'], uuid_s3, metrica_cpf)

    if metrica_cpf >= 0.30:
        output_object['VALIDAR_CPF'] = True
    else:
        output_object['VALIDAR_CPF'] = False


    metrica_rg = SequenceMatcher(None, RG, message['DOC_NUMBER']['RG']).ratio()
    inserir_resultado_ia(message['DOC_TYPE'], message['DOC_NUMBER']['RG'], RG, 'RG', message['FILE'], uuid_s3, metrica_rg)
    if metrica_rg >= 0.30:
        output_object['VALIDAR_RG'] = True
    else:
        output_object['VALIDAR_RG'] = False


    metrica_cnh = SequenceMatcher(None, CNH, message['DOC_NUMBER']['CNH']).ratio()
    inserir_resultado_ia(message['DOC_TYPE'], message['DOC_NUMBER']['CNH'], CNH, 'CNH', message['FILE'], uuid_s3, metrica_cnh)

    if  metrica_cnh >= 0.30:
        output_object['VALIDAR_CNH'] = True
    else:
        output_object['VALIDAR_CNH'] = False



    output_object['VALIDAR_DOCUMENTO'] = validar_documento

    return output_object, {'CNH_FRENTE':CNH_FRENTE, 'CNH_VERSO':CNH_VERSO, 'CNH': CNH, 'NOME':NOME, 'RG': RG, 'CPF': CPF, 'DATA_NASCIMENTO': DATA_NASCIMENTO}


def process_CPF_predicition(message, results, output_object):
    classes = ['CPF_FRENTE', 'CPF', 'NOME', 'CPF_ANTIGO_FRENTE', 'CPF_ANTIGO_NUMERO', 'CPF_ANTIGO_NOME']
    results['labels'] = results.apply(lambda row: classes[int(row['labels'])], axis=1)

    valaildar_documento = True

    CPF_FRENTE = verify_object_existence(results[results['labels'] == 'CPF_FRENTE'])
    CPF = extract_data_from_prediction(message, results[results['labels'] == 'CPF'])
    NOME = extract_data_from_prediction(message, results[results['labels'] == 'NOME'])

    CPF_ANTIGO_FRENTE = verify_object_existence(results[results['labels'] == 'CPF_ANTIGO_FRENTE'])
    CPF_ANTIGO_NUMERO = extract_data_from_prediction(message, results[results['labels'] == 'CPF_ANTIGO_NUMERO'])
    CPF_ANTIGO_NOME = extract_data_from_prediction(message, results[results['labels'] == 'CPF_ANTIGO_NOME'])

    if NOME==message['DOC_NUMBER']['NOME'] or CPF_ANTIGO_NOME==message['DOC_NUMBER']['NOME']:
        output_object['VALIDAR_NOME'] = True
    else:
        output_object['VALIDAR_NOME'] = False
        valaildar_documento = False

    if CPF == message['DOC_NUMBER']['CPF'] or CPF_ANTIGO_NUMERO == message['DOC_NUMBER']['CPF']:
        output_object['VALIDAR_CPF'] = True
    else:
        output_object['VALIDAR_CPF'] = False
        valaildar_documento = False

    if CPF_FRENTE == True or CPF_ANTIGO_FRENTE == True:
        output_object['VALIDAR_FRENTE_VERSO'] = True
    else:
        output_object['VALIDAR_FRENTE_VERSO'] = False
        valaildar_documento = False

    output_object['VALIDAR_DOCUMENTO'] = valaildar_documento

    return output_object, {'CPF_FRENTE':CPF_FRENTE, 'CPF':CPF, 'NOME': NOME, 'CPF_ANTIGO_FRENTE':CPF_ANTIGO_FRENTE, 'CPF_ANTIGO_NUMERO': CPF_ANTIGO_NUMERO, 'CPF_ANTIGO_NOME': CPF_ANTIGO_NOME}


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
