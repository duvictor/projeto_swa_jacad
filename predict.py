from src.model_manager import load_model, process_prediction
from src.file_manager import check_file_integrity, read_image

def create_output_object():
    object = {
        'VALIDAR_DOCUMENTO': '',
        'MENSAGENS': '',
        'VALIDAR_NOME': '',
        'VALIDAR_FRENTE_VERSO': '',
        'VALIDAR_NUMERO': '',
        'VALIDAR_DATA_NASCIMENTO': '',
        'VALIDAR_DIPLOMA_NOME': '',
        'VALIDAR_DIPLOMA_GRAU': '',
        'VALIDAR_DIPLOMA_COLACAO': '',
        'VALIDAR_DIPLOMA_COLACAO_POSTERIOR': '',
        'VALIDAR_DIPLOMA_RESTRICOES': '',
        'VALIDAR_DIPLOMA_CORROMPIDO': '',
        'VALIDAR_CERTIDAO_NOME': '',
        'VALIDAR_CERTIDAO_GRAU': '',
        'VALIDAR_CERTIDAO_COLACAO': '',
        'VALIDAR_CERTIDAO_COLACAO_POSTERIOR': '',
        'VALIDAR_CERTIDAO_RESTRICOES': '',
        'VALIDAR_CERTIDAO_CORROMPIDO': '',
        'VALIDAR_CERTIDAO_EMISSAO': ''
    }

    return object

def process_output(message=None, output_message=None, invalid_file=False):


    if invalid_file:
        return ['O arquivo do documento de identificação está corrompido ou protegido por senha']

    errors = list()
    if message['DOC_TYPE'] == 'RG':

        if message['DOC_NUMBER']['RG_NOME'] != '':
            if not message['DOC_NUMBER']['RG_NOME'] == output_message['RG_NOME']:
                errors.append('Seu nome está diferente do documento.')


        if message['DOC_NUMBER']['RG_NUMERO'] != '':
            if not message['DOC_NUMBER']['RG_NUMERO'] == output_message['RG_NUMERO']:
                errors.append('O número do RG é divergente do nome informado no cadastro.')


        if message['DOC_NUMBER']['RG_CPF'] != '':
            if not message['DOC_NUMBER']['RG_CPF'] == output_message['RG_CPF']:
                errors.append('O número do CPF é divergente do nome informado no cadastro.')


        if not output_message['RG_NASCIMENTO']:
            errors.append('Documento ilegível ou cortado. não é possivel identificar a data de nascimento')


    elif message['DOC_TYPE'] == 'CNH':

        if message['DOC_NUMBER']['CNH_NOME'] != '':
            if not message['DOC_NUMBER']['CNH_NOME'] == output_message['CNH_NOME']:
                errors.append('Seu nome está diferente do documento.')



        if message['DOC_NUMBER']['CNH_NUMERO'] != '':
            if not message['DOC_NUMBER']['CNH_NUMERO'] == output_message['CNH_NUMERO']:
                errors.append('O número da CNH é divergente do nome informado no cadastro.')


        if message['DOC_NUMBER']['RG_NUMERO'] != '':
            if not message['DOC_NUMBER']['RG_NUMERO'] == output_message['RG_NUMERO']:
                errors.append('O número do RG é divergente do nome informado no cadastro.')


        if message['DOC_NUMBER']['CPF_NUMERO'] != '':
            if not message['DOC_NUMBER']['CPF_NUMERO'] == output_message['CPF_NUMERO']:
                errors.append('O número do CPF é divergente do nome informado no cadastro.')


    return errors


def make_prediction(message):
    """"
    message = {
        DOC_TYPE:   document type to be validated
        FILE_PATH:  path to file
        DOC_NUMBER: user provided document number
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
        img, scale   = read_image(message)

        boxes, scores, labels = model.predict_on_batch(img)
        boxes /= scale

        output_object = create_output_object()

        output_object, output_message = process_prediction(message, boxes, scores, labels, output_object)
        print(output_message)

        errors = process_output(message, output_message)

        output_object['MENSAGENS'] = errors

    return output_object

#m = {
#        'DOC_TYPE':  'CNH',
#        'FILE_PATH': r'C:\Bloomia\data\Treino\CNH\Train\Alysson CNH.jpg',
#        'DOC_NUMBER': {'RG_NOME': 'JOAO', 'RG_NUMERO': '123', 'RG_CPF': ''}
#    }

#m = {
#        'DOC_TYPE':  'RG',
#        'FILE_PATH': r'C:\Bloomia\data\Treino\CNH\Train\Alysson CNH.jpg',
#        'DOC_NUMBER': {'CNH_NOME': 'JOAO', 'CNH_NUMERO': '123', 'RG_NUMERO': '', 'CPF_NUMERO': ''}
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
objeto_recebido = { 'RG_FRENTE': True,
                   'RG_VERSO': True,
                   'RG_NUMERO': 4422428,
                   'RG_NOME': 'JOSE',
                   'RG_NASCIMENTO': '01/01/1990',
                   'RG_CPF': '012.345.678-00',
                   'CPF_FRENTE': True,
                   'CPF_NUMERO': '012.345.678-00',
                   'CPF_NOME': 'JOSE',
                   'CPF_ANTIGO_FRENTE':  True,
                   'CPF_ANTIGO_NUMERO': True,
                   'CPF_ANTIGO_NOME': 'JOSE',
                   'CNH_FRENTE': True,
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