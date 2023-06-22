import datetime
import json
import cv2
import numpy as np
from flask import Flask, request
from flask_restx import Resource, Api, reqparse
from werkzeug.datastructures import FileStorage
from utils import process_args, check_file
from predict import make_prediction


TOKEN_LOCAL = '1234567890'

app = Flask(__name__)

api = Api(app, title='API Mock integração Jacad', version='1.0', description='Api de integração com python flask', prefix='/api')


# https://flask-restx.readthedocs.io/en/latest/parsing.html
# https://flask.palletsprojects.com/en/2.3.x/patterns/fileuploads/
# documentação indicando como fazer
upload_parser = api.parser()
upload_parser.add_argument('documento',
    location='files', 
    type=FileStorage, 
    required=True, 
    help='Arquivo que será predito pela inteligência artificial')


upload_parser.add_argument('tipo', required=True, help='Tipo do documento: cpf, rg, cnh')
upload_parser.add_argument('objeto', required=True, help='objeto com as informações necessárias a serem validadas, conforme demonstrado no swagger')




@api.route("/")
class Home(Resource):
    def get(self):
        '''
        responsavel por testar a api de integracao e verificar se o sistema está ativo
        :return:
        '''
        tz = datetime.timezone.utc
        ft = "%Y-%m-%d"
        return {'ativo': datetime.datetime.now(tz=tz).strftime(ft)}, 200


@api.route('/hello')
class HelloWorld(Resource):
    def get(self):
        '''
        responsavel por testar a disponibilidade da integração
        :return:
        '''
        return {'hello': 'world'}


@api.route('/upload/')
@api.expect(upload_parser)
class Upload(Resource):
    def post(self):
        '''
        responsavel por receber um arquivo no formato jpg ou pdf
        o tipo do documento: cpf, rg, cnh.
        E responder o recebimento do arquivo
        simulando o comportamento da IA.

        formato do objeto esperado no payload
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



        
        * autenticacao basic, usando o beaurus manda no header.
        * para testar usando postman:
            http://localhost:5000/api/upload/

            {
    "file": ["C:/Bloomia/Cópia de RG_2.jpg"],
    "tipo": ["RG"],
    "objeto": [{
        "RG_FRENTE": true,
        "RG_VERSO": true,
        "RG_NUMERO": 4422428,
        "RG_NOME": "JOSE",
        "RG_NASCIMENTO": "01/01/1990",
        "RG_CPF": "012.345.678-00",
        "CPF_FRENTE": true,
        "CPF_NUMERO": "012.345.678-00",
        "CPF_NOME": "JOSE",
        "CPF_ANTIGO_FRENTE": true,
        "CPF_ANTIGO_NUMERO": true,
        "CPF_ANTIGO_NOME": "JOSE",
        "CNH_FRENTE": true,
        "CNH_NUMERO": "123456789011",
        "CNH_NOME": "JOSE",
        "RNE_NUMERO": "12345678901122445",
        "RNE_NOME": "JOSE",
        "PASSAPORTE_NOME": "JOSE",
        "PASSAPORTE_NUMERO": "123456789011",
        "DIPLOMA_NOME": "JOSE",
        "DIPLOMA_GRAU": "bacharelado",
        "DIPLOMA_DATA_COLACAO": "01/01/1990",
        "CERTIDAO_NOME": "JOSE",
        "CERTIDAO_GRAU": "bacharelado",
        "CERTIDAO_DATA_COLACAO": "01/01/1990"
    }]
}


        :return:

        objeto_retorno = {
                    'VALIDAR DOCUMENTO: True,
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
        '''

        errors_message = list()

        try:
            headers = request.headers
            bearer = headers.get('Authorization')  # Bearer YourTokenHere
            token = bearer.split()[0]  # YourTokenHere

            if token != TOKEN_LOCAL:
                errors_message.append({'erro': 'Falha de autorização'}, 400)
                return errors_message


            args = upload_parser.parse_args()
            #args = self.api.payload
            uploaded_file = args['documento']  # This is FileStorage instance
            type_file = args['tipo']
            object_parameter = args['objeto']
            json_object = json.loads(object_parameter)

            imagem = cv2.imdecode(np.frombuffer(uploaded_file.read(), np.uint8), cv2.IMREAD_UNCHANGED)
            errors_message.append(check_file(uploaded_file, type_file))

        except Exception as erro:
            print(erro)
            errors_message.append({'erro': 'Arquivo não recebido'}, 400)
            return errors_message

        # uploaded_file, type_file, objeto_json
        message = process_args(uploaded_file.filename, imagem, type_file, json_object)
        output_message = make_prediction(message)

        if len(errors_message) != 0:
            output_message['MENSAGENS'].append(errors_message)

        print(output_message)

        return output_message


if __name__ == '__main__':
    app.run("0.0.0.0", 3000, threaded=True)

