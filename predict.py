from src.cnh_manager import process_prediction_cnh
from src.model_manager import process_prediction
from src.model_utils import load_model
from src.file_manager import check_file_integrity, read_image
#usado para verificar a similaridade de strings, solução paleativa até que o ocr esteja 100%
from difflib import SequenceMatcher


def process_output(message=None, output_message=None):


    errors = list()
    if message['DOC_TYPE'] == 'RG':

        if not output_message['NOME']:
            errors.append('Seu nome está diferente do documento ou não está legível no documento.')

        if not output_message['RG']:
            errors.append('O número do RG é divergente do número informado no cadastro ou não está legível.')

        if message['DOC_NUMBER']['CPF'] != '':
            if not output_message['CPF']:
                errors.append('O número do CPF é divergente do número informado no cadastro ou não está legível')

        if not output_message['DATA_NASCIMENTO']:
            errors.append('Documento ilegível ou cortado. Não é possível identificar a data de nascimento')

    elif message['DOC_TYPE'] == 'CNH':
        'validar nome e cpf'

        # if output_message['CNH_NOME'] != '':
        #     if SequenceMatcher(None, output_message['CNH_NOME'], message['DOC_NUMBER']['CNH_NOME']).ratio() <= 0.30:
        #         errors.append('Seu nome está diferente do documento.')
        # else:
        #     errors.append('Seu nome não está legível no documento.')

        if output_message['CNH'] != '':
            if SequenceMatcher(None, output_message['CNH'], message['DOC_NUMBER']['CNH']).ratio() <= 0.50:
                errors.append('O número da CNH é divergente do número informado no cadastro.')
        else:
            errors.append('O número de CNH não está legível.')

        if message['DOC_NUMBER']['RG'] != '':
            if output_message['RG'] != '':
                if SequenceMatcher(None, output_message['RG'], message['DOC_NUMBER']['RG']).ratio() <= 0.50:
                    errors.append('O número do RG é divergente do número informado no cadastro.')
            else:
                errors.append('O usuário informou o número de RG junto com a CNH, porém o número de RG não está legível.')

        if message['DOC_NUMBER']['CPF'] != '':
            if output_message['CPF'] != '':
                if SequenceMatcher(None, output_message['CPF'], message['DOC_NUMBER']['CPF']).ratio() <= 0.50:
                    errors.append('O número do CPF é divergente do número informado no cadastro.')
            else:
                errors.append('O usuário informou o número de CPF junto com a CNH, porém o número de CPF não está legível.')

    elif message['DOC_TYPE'] == 'CPF':

        if output_message['CPF_NOME'] != '':
            if SequenceMatcher(None, output_message['CPF_NOME'], message['DOC_NUMBER']['CPF_NOME']).ratio() <= 0.30:
                errors.append('Seu nome está diferente do documento.')
        else:
            errors.append('Seu nome não está legível no documento.')

        if output_message['CPF'] != '':
            if SequenceMatcher(None, output_message['CPF'], message['DOC_NUMBER']['CPF']).ratio() <= 0.30:
                errors.append('O número do CPF é divergente do número informado no cadastro.')
        else:
            errors.append('O número de CPF não está legível.')




    elif message['DOC_TYPE'] == 'DIPLOMA':

        if output_message['DOC_NOME'] != '':
            if not message['DOC_NUMBER']['DOC_NOME'] == output_message['DOC_NOME']:
                errors.append('Seu nome está diferente do documento.')
        else:
            errors.append('Seu nome não está legível no documento.')

        if output_message['DOC_GRAU'] != '':
            if not message['DOC_NUMBER']['DOC_GRAU'] == output_message['DOC_GRAU']:
                errors.append('O grau do certificado é diferente do informado.')
            else:
                if output_message['VALIDAR_RESTRICOES_GRAU_BLT'] == False:
                    errors.append('É necessário que seja Diploma do Ensino Superior com título de Bacharel, Licenciatura ou Tecnólogo.')

                if output_message['VALIDAR_RESTRICOES_GRAU_SFE'] == False:
                    errors.append('O curso informado não é permitido para solicitação de pós-graduação.')
        else:
            errors.append('O grau não está legível no documento.')

        if output_message['DOC_DATA_COLACAO'] != '':
            if not output_message['DOC_DATA_COLACAO'] == message['DOC_NUMBER']['DOC_DATA_COLACAO']:
                errors.append('A data de colação no documento é divergente da data informada.')
            else:
                if not output_message['VALIDAR_DATA_COMPRA']:
                    errors.append('A data de colação de grau é posterior a data de compra.')
        else:
            errors.append('A data de colação não está legível no documento.')

        if output_message['DOC_GRAU'] != '':
            if not message['DOC_NUMBER']['DOC_GRAU'] == output_message['DOC_GRAU']:
                errors.append('O grau do certificado é diferente do informado.')
            else:
                if output_message['VALIDAR_RESTRICOES_GRAU'] == False:
                    errors.append('É necessário que seja Diploma do Ensino Superior com título de Bacharel, Licenciatura ou Tecnólogo.')



    elif message['DOC_TYPE'] == 'CERTIFICADO':
        if output_message['DOC_NOME'] != '':
            if not message['DOC_NUMBER']['DOC_NOME'] == output_message['DOC_NOME']:
                errors.append('Seu nome está diferente do documento.')
        else:
            errors.append('Seu nome não está legível no documento.')


        if output_message['DOC_GRAU'] != '':
            if not message['DOC_NUMBER']['DOC_GRAU'] == output_message['DOC_GRAU']:
                errors.append('O grau do certificado é diferente do informado.')
            else:
                if output_message['VALIDAR_RESTRICOES_GRAU_BLT'] == False:
                    errors.append('É necessário que seja Diploma do Ensino Superior com título de Bacharel, Licenciatura ou Tecnólogo.')

                if output_message['VALIDAR_RESTRICOES_GRAU_SFE'] == False:
                    errors.append('O curso informado  não é permitido para solicitação de pós-graduação.')
        else:
            errors.append('O grau não está legível no documento.')

        if output_message['DOC_DATA_COLACAO'] != '':
            if not message['DOC_NUMBER']['DOC_DATA_COLACAO'] == output_message['DOC_DATA_COLACAO']:
                errors.append('A data da colação é diferente da informada.')
            else:
                if not output_message['VALIDAR_DATA_COMPRA']:
                    errors.append('A data de colação de grau é posterior a data de compra.')
        else:
            errors.append('A data de colação não está legível no documento.')

        if output_message['DOC_DATA_EMISSAO'] != '':
            if not message['DOC_NUMBER']['DOC_DATA_EMISSAO'] == output_message['DOC_DATA_EMISSAO']:
                errors.append('A data da emissão do certificado/certidão é diferente da informada.')
        else:
            errors.append('A data de emissão não está legível no documento.')

        if output_message['DOC_DATA_EMISSAO'] != '' and output_message['DOC_DATA_EMISSAO'] != '':
            if message['DOC_NUMBER']['DOC_DATA_COLACAO'] == output_message['DOC_DATA_COLACAO'] and message['DOC_NUMBER']['DOC_DATA_EMISSAO'] == output_message['DOC_DATA_EMISSAO']:
                if output_message['VALIDAR_RESTRICAO_DATA_EMISSAO_COLACAO'] == False:
                    errors.append('A data de emissão do documento não pode ser superior a 1 ano da data da colação atual.')
                if output_message['VALIDAR_RESTRICAO_DATA_EMISSAO_HOJE'] == False:
                    errors.append('Data de emissão do certificado de colação de grau está fora do prazo permitido (até 1 ano antes da data atual).')



    #   elif message['DOC_TYPE'] == 'RNE':
    #
    #       if message['DOC_NUMBER']['RNE_NOME'] != '':
    #           if not message['DOC_NUMBER']['RNE_NOME'] == output_message['RNE_NOME']:
    #               errors.append('Seu nome está diferente do documento.')
    #
    #       if message['DOC_NUMBER']['RNE_NUMERO'] != '':
    #           if not message['DOC_NUMBER']['RNE_NUMERO'] == output_message['RNE_NUMERO']:
    #               errors.append('O número do RNE é divergente do número informado no cadastro.')
    #
    #   elif message['DOC_TYPE'] == 'PASSAPORTE':
    #
    #       if message['DOC_NUMBER']['PASSAPORTE_NOME'] != '':
    #           if not message['DOC_NUMBER']['PASSAPORTE_NOME'] == output_message['PASSAPORTE_NOME']:
    #               errors.append('Seu nome está diferente do documento.')
    #
    #
    #       if message['DOC_NUMBER']['PASSAPORTE_NUMERO'] != '':
    #           if not message['DOC_NUMBER']['PASSAPORTE_NUMERO'] == output_message['PASSAPORTE_NUMERO']:
    #               errors.append('O número do PASSAPORTE é divergente do número informado no cadastro.')

    return errors


def make_prediction(message, output_object):
    """"
message = {'DOC_TYPE': 'PASSAPORTE',
                   'FILE': file_name,
                   'IMAGE': uploaded_file,
                   'DOC_NUMBER': {'PASSAPORTE_NOME':   objeto_json['PASSAPORTE_NOME'],
                                  'PASSAPORTE_NUMERO': objeto_json['PASSAPORTE_NUMERO'],

          }
    """

    # if check_file_integrity(message['FILE_PATH']):
    #     # Return message of not valid file
    #     print('Invalid File')
    #     errors =  process_output(invalid_file=True)

    if False:
        a = 45
    else:

        model = load_model(message)
        img, scale = read_image(message)

        boxes, scores, labels = model.predict_on_batch(img)
        boxes /= scale

        output_object, output_message = process_prediction(message, boxes, scores, labels, output_object)
        print(output_message)

        errors = process_output(message, output_message)

        output_object['MENSAGENS'] = errors

    return output_object


def make_prediction_cnh(message, output_object):
    retorno_qualquer = process_prediction_cnh(message)

    return output_object

#m = {
#        'DOC_TYPE':  'CNH',
#        'FILE_PATH': r'C:\Bloomia\data\Treino\CNH\Train\Alysson CNH.jpg',
#        'DOC_NUMBER': {'RG_NOME': 'JOAO', 'RG_NUMERO': '123', 'RG_CPF': ''}
#    }

#m = {
#        'DOC_TYPE':  'RG',
#        'FILE_PATH': r'C:\Bloomia\data\Treino\CNH\Train\Alysson CNH.jpg',
#        'DOC_NUMBER': {'NOME': 'JOAO', 'CNH': '123', 'RG': '', 'CPF': ''}
#    }
#
#make_prediction(m)


'''
responsavel por manter padrões do sistema
1 = só aceitar rg com frente e verso na mesma foto
2 = a imagens grandes e nítidas, mínino 1024 por 1080
'''

""""
tipos_documentos ={'RG', 'CNH,', 'PASSAPORTE', 'RNE', 'DIPLOMA', 'CERTIDAO'}
objeto_recebido = { 
                   'RG': 4422428,
                   'RG_NOME': 'JOSE',
                   'RG_NASCIMENTO': '01/01/1990',
                   'CPF': '012.345.678-00',
                   'CPF': '012.345.678-00',
                   'CPF_NOME': 'JOSE',
                   'CPF_ANTIGO_FRENTE':  True,
                   'CPF_ANTIGO_NUMERO': True,
                   'CPF_ANTIGO_NOME': 'JOSE',
                   'CNH_NUMERO': '123456789011',
                   'CNH_NOME': 'JOSE',
                   'RNE_NUMERO': '12345678901122445',
                   'RNE_NOME': 'JOSE',
                   'PASSAPORTE_NOME': 'JOSE',
                   'PASSAPORTE_NUMERO': '123456789011',
                   'DIPLOMA_NOME': 'JOSE',
                   'DIPLOMA_GRAU' : 'bacharelado',
                   'DIPLOMA_DATA_COLACAO': '01/01/1990',
                   'CERTIDAO_NOME': 'JOSE',
                   'CERTIDAO_GRAU' : 'bacharelado',
                   'CERTIDAO_DATA_COLACAO': '01/01/1990'
                   'CERTIDAO_DATA_EMISSAO': '01/02/1990'
                   }


objeto_retorno = {
                   'VALIDAR_NOME': True,
                  'VALIDAR_FRENTE_VERSO': True,
                  'VALIDAR_NUMERO': True,
                  'VALIDAR_DATA_NASCIMENTO': True,

                   # - Validar nome.
                  'VALIDAR_DIPLOMA_NOME': True,
                   # - Grau
                  'VALIDAR_DIPLOMA_GRAU' : True,
                   # Data colação:
                  'VALIDAR_DIPLOMA_COLACAO' : True,
                   # Validar se a data de colação é posterior à compra da pós-graduação
                  'VALIDAR_DIPLOMA_COLACAO_POSTERIOR' : True,
                   # Não pode contar as palavras:
                  'VALIDAR_DIPLOMA_RESTRICOES' :  True,
                   # O arquivo do diploma está corrompido ou protegido por senha
                   'VALIDAR_DIPLOMA_CORROMPIDO' :  True,
                   'VALIDAR_CERTIDAO_NOME': True,
                  'VALIDAR_CERTIDAO_GRAU' : True,
                  'VALIDAR_CERTIDAO_COLACAO' : True,
                  'VALIDAR_CERTIDAO_COLACAO_POSTERIOR' : True,
                  'VALIDAR_CERTIDAO_RESTRICOES' :  True,
                   'VALIDAR_CERTIDAO_CORROMPIDO' :  True,
                   # Exclusivamente para a certidão/declaração de conclusão
                   'VALIDAR_CERTIDAO_EMISSAO' :  True

   }
"""