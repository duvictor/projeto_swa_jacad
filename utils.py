'''
responsavel por manter padrões do sistema
1 = só aceitar rg com frente e verso na mesma foto
2 = a imagens grandes e nítidas, mínino 1024 por 1080
'''


def process_args(file_name, uploaded_file, type_file, objeto_json):
    # uploaded_file = args['file'][0]  # This is FileStorage instance
    # type_file     = args['tipo'][0]
    # objeto_json   = args['objeto'][0]

    if type_file == 'RG':
        message = {'DOC_TYPE':   'RG',
                   'FILE': file_name,
                   'IMAGE':  uploaded_file,
                   'DOC_NUMBER': {'RG_NOME': objeto_json['RG_NOME'],
                                  'RG_NUMERO': objeto_json['RG_NUMERO'],
                                  'RG_CPF': objeto_json['RG_CPF'],
                                 }
                   }
    elif type_file == 'CNH':
        message = {'DOC_TYPE': 'CNH',
                   'FILE': file_name,
                   'IMAGE': uploaded_file,
                   'DOC_NUMBER': {'CNH_NOME': objeto_json['CNH_NOME'],
                                  'CNH_NUMERO': objeto_json['CNH_NUMERO'],
                                  'RG_NUMERO': objeto_json['RG_NUMERO'],
                                  'CPF_NUMERO': objeto_json['CPF_NUMERO'],
                                  }
                   }

    elif type_file == 'CPF':
        message = {'DOC_TYPE': 'CPF',
                   'FILE': file_name,
                   'IMAGE': uploaded_file,
                   'DOC_NUMBER': {'CPF_FRENTE': objeto_json['CPF_FRENTE'],
                                  'CPF_NUMERO': objeto_json['CPF_NUMERO'],
                                  'CPF_NOME':   objeto_json['CPF_NOME'],
                                  'CPF_ANTIGO_FRENTE': objeto_json['CPF_ANTIGO_FRENTE'],
                                  'CPF_ANTIGO_NUMERO': objeto_json['CPF_ANTIGO_NUMERO'],
                                  'CPF_ANTIGO_NOME':   objeto_json['CPF_ANTIGO_NOME'],
                                  }
                   }

    elif type_file == 'RNE':
        message = {'DOC_TYPE': 'RNE',
                   'FILE': file_name,
                   'IMAGE': uploaded_file,
                   'DOC_NUMBER': {'RNE_NUMERO': objeto_json['RNE_NUMERO'],
                                  'RNE_NOM':    objeto_json['RNE_NOME'],

                                  }
                   }

    elif type_file == 'PASSAPORTE':
        message = {'DOC_TYPE': 'PASSAPORTE',
                   'FILE': file_name,
                   'IMAGE': uploaded_file,
                   'DOC_NUMBER': {'PASSAPORTE_NOME':   objeto_json['PASSAPORTE_NOME'],
                                  'PASSAPORTE_NUMERO': objeto_json['PASSAPORTE_NUMERO'],

                                  }
                   }

    elif type_file == 'PASSAPORTE':
        message = {'DOC_TYPE': 'PASSAPORTE',
                   'FILE': file_name,
                   'IMAGE': uploaded_file,
                   'DOC_NUMBER': {'PASSAPORTE_NOME':   objeto_json['PASSAPORTE_NOME'],
                                  'PASSAPORTE_NUMERO': objeto_json['PASSAPORTE_NUMERO'],

                                  }
                   }

    elif type_file == 'DIPLOMA_CERTIDAO':
        message = {'DOC_TYPE': 'DIPLOMA_CERTIDAO',
                   'FILE': file_name,
                   'IMAGE': uploaded_file,
                   'DOC_NUMBER': {'DIPLOMA_NOME':   objeto_json['DIPLOMA_NOME'],
                                  'DIPLOMA_GRAU': objeto_json['DIPLOMA_GRAU'],
                                  'DIPLOMA_DATA_COLACAO': objeto_json['DIPLOMA_DATA_COLACAO'],
                                  'CERTIDAO_NOME': objeto_json['CERTIDAO_NOME'],
                                  'CERTIDAO_GRAU': objeto_json['CERTIDAO_GRAU'],
                                  'CERTIDAO_DATA_COLACAO': objeto_json['CERTIDAO_DATA_COLACAO'],
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