'''
responsavel por manter padrões do sistema
1 = só aceitar rg com frente e verso na mesma foto
2 = a imagens grandes e nítidas, mínino 1024 por 1080
'''

from dateutil.parser import parse
from datetime import datetime
from unidecode import unidecode
from pdf2jpg import pdf2jpg
import os

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
        'VALIDAR_CERTIDAO_NOME': '',
        'VALIDAR_CERTIDAO_GRAU': '',
        'VALIDAR_CERTIDAO_COLACAO': '',
        'VALIDAR_CERTIDAO_EMISSAO': '',
        'VALIDAR_RESTRICAO_CERTIDAO_DATA_EMISSAO_COLACAO': '',
        'VALIDAR_RESTRICAO_CERTIDAO_DATA_EMISSAO_HOJE': '',
        'VALIDAR_RESTRICOES_GRAU_BLT': '',
        'VALIDAR_RESTRICOES_GRAU_SFE': '',
        'VALIDAR_CORROMPIDO': '',
        'VALIDAR_DATA_COMPRA': ''
    }
    return object

def processa_str(texto):
    caracteres_permitidos = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 "
    texto_sem_especiais = ''.join(caractere for caractere in unidecode(str(texto)) if caractere in caracteres_permitidos)
    return str.lower(texto_sem_especiais)


def parse_data_pt_br(data_texto):
    meses_pt_br = {
        'Janeiro': '01',
        'Fevereiro': '02',
        'Março': '03',
        'Abril': '04',
        'Maio': '05',
        'Junho': '06',
        'Julho': '07',
        'Agosto': '08',
        'Setembro': '09',
        'Outubro': '10',
        'Novembro': '11',
        'Dezembro': '12',
        'janeiro': '01',
        'fevereiro': '02',
        'março': '03',
        'abril': '04',
        'maio': '05',
        'junho': '06',
        'julho': '07',
        'agosto': '08',
        'setembro': '09',
        'outubro': '10',
        'novembro': '11',
        'dezembro': '12'
    }

    for mes_pt_br, mes_num in meses_pt_br.items():
        data_texto = data_texto.replace(mes_pt_br, mes_num)

    try:
        data_obj = datetime.strptime(data_texto, '%d de %m de %Y')
        return data_obj
    except ValueError:
        raise ValueError("Formato de data em português inválido.")


def converter_data_pt_br(data_texto):
    try:
        data_obj = parse(data_texto)
        return data_obj
    except ValueError:
        try:
            data_obj = parse_data_pt_br(data_texto)
            return data_obj
        except ValueError as e:
            raise ValueError(str(e) + " Tente fornecer uma data válida em formato DD/MM/YYYY ou mês por extenso.")

def calcular_intervalo_um_ano(data1, data2):
    # Converter as datas para objetos datetime
    try:
        data1_obj = converter_data_pt_br(data1)
        data2_obj = converter_data_pt_br(data2)
    except ValueError:
        return ValueError

    # Calcular a diferença entre as duas datas
    diferenca = (data2_obj - data1_obj).days

    # Verificar se o intervalo é de até um ano (aproximadamente 365 dias)
    if diferenca > 365:
        return True
    else:
        return False

def verificar_data_compra(data_compra, data_colacao):
    # Converter as datas para objetos datetime
    try:
        data_compra_obj = converter_data_pt_br(data_compra)
        data_colacao_obj = converter_data_pt_br(data_colacao)
    except ValueError:
        return ValueError

    # Calcular a diferença entre as duas datas
    diferenca = (data_colacao_obj - data_compra_obj).days

    # Verificar se a data da compra é posterior a data de colacao
    if diferenca < 0:
        return False
    else:
        return True


def process_args(file_name, uploaded_file, type_file, objeto_json):
    # uploaded_file = args['file'][0]  # This is FileStorage instance
    # type_file     = args['tipo'][0]
    # objeto_json   = args['objeto'][0]

    if type_file == 'RG':
        message = {'DOC_TYPE':   'RG',
                   'FILE': file_name,
                   'IMAGE':  uploaded_file,
                   'DOC_NUMBER': {'NOME': processa_str(objeto_json['NOME']),
                                  'RG': processa_str(objeto_json['RG']),
                                  'CPF': processa_str(objeto_json['CPF']),
                                 }
                   }
    elif type_file == 'CNH':
        message = {'DOC_TYPE': 'CNH',
                   'FILE': file_name,
                   'IMAGE': uploaded_file,
                   'DOC_NUMBER': {'NOME': processa_str(objeto_json['NOME']),
                                  'CNH': processa_str(objeto_json['CNH']),
                                  'RG': processa_str(objeto_json['RG']),
                                  'CPF': processa_str(objeto_json['CPF']),
                                  }
                   }

    elif type_file == 'CPF':
        message = {'DOC_TYPE': 'CPF',
                   'FILE': file_name,
                   'IMAGE': uploaded_file,
                   'DOC_NUMBER': {'NOME':   processa_str(objeto_json['NOME']),
                                  'CPF': processa_str(objeto_json['CPF'])
                                  }
                   }

    elif type_file == 'RNE':
        message = {'DOC_TYPE': 'RNE',
                   'FILE': file_name,
                   'IMAGE': uploaded_file,
                   'DOC_NUMBER': {'RNE': processa_str(objeto_json['RNE']),
                                  'NOME':    processa_str(objeto_json['NOME']),

                                  }
                   }

    elif type_file == 'PASSAPORTE':
        message = {'DOC_TYPE': 'PASSAPORTE',
                   'FILE': file_name,
                   'IMAGE': uploaded_file,
                   'DOC_NUMBER': {'NOME':   processa_str(objeto_json['NOME']),
                                  'PASSAPORTE': processa_str(objeto_json['PASSAPORTE']),

                                  }
                   }

    elif type_file == 'DIPLOMA':
        message = {'DOC_TYPE': 'DIPLOMA',
                   'FILE': file_name,
                   'IMAGE': uploaded_file,
                   'DOC_NUMBER': {'DOC_NOME':   processa_str(objeto_json['DIPLOMA_NOME']),
                                  'DOC_GRAU': processa_str(objeto_json['DIPLOMA_GRAU']),
                                  'DOC_DATA_COLACAO': objeto_json['DIPLOMA_DATA_COLACAO'],
                                  'DATA_COMPRA': objeto_json['DATA_COMPRA']
                                  }
                   }

    elif type_file == 'CERTIDAO' or type_file == 'CERTIFICADO':
        message = {'DOC_TYPE': 'CERTIFICADO',
                   'FILE': file_name,
                   'IMAGE': uploaded_file,
                   'DOC_NUMBER': {'DOC_NOME': processa_str(objeto_json['CERTIDAO_NOME']),
                                  'DOC_GRAU': processa_str(objeto_json['CERTIDAO_GRAU']),
                                  'DOC_DATA_COLACAO': objeto_json['CERTIDAO_DATA_COLACAO'],
                                  'DOC_DATA_EMISSAO': objeto_json['CERTIDAO_DATA_EMISSAO'],
                                  'DATA_COMPRA': objeto_json['DATA_COMPRA']
                                  }
                   }

    else:
        raise ValueError("Invalid Document Type Provided on Message")

    return message


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'jpeg', 'pdf'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def check_file(uploaded_file, type_file):
    if(allowed_file(uploaded_file)):
        token = '1234567'
        return {'sucesso': 'Arquivo recebido com sucesso!', 'token': token, "tipo": type_file}, 201


tipos_documentos ={'RG', 'CNH,', 'PASSAPORTE', 'RNE', 'DIPLOMA', 'CERTIDAO'}


objeto_recebido = { 'RG_FRENTE': True,
                    'RG_VERSO': True,
                    'RG': 4422428,
                    'NOME': 'JOSE',
                    'DATA_NASCIMENTO': '01/01/1990',
                    'CPF_FRENTE': True,
                    'CPF': '012.345.678-00',
                    'CPF_ANTIGO_FRENTE':  True,
                    'CPF_ANTIGO_NUMERO': True,
                    'CPF_ANTIGO_NOME': 'JOSE',
                    'CNH_FRENTE': True,
                    'CNH': '123456789011',
                    'RNE': '12345678901122445',
                    'PASSAPORTE': '123456789011',
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



def converterPdf(inputpath, outputpath):
    '''
    responsavel por converter pdf para imagem
    :param inputpath:
    :param outputpath:
    :return:
    '''
    print('*' * 30)
    print('INICIANDO CONVERSAO')
    print('*' * 30)
    result = pdf2jpg.convert_pdf2jpg(inputpath, outputpath, pages="ALL")
    print('*' * 30)
    print('CONVERSAO FINALIZADA')
    print('*' * 30)
    return result