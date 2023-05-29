import datetime

from flask import Flask, request
from flask_restx import Resource, Api
from werkzeug.datastructures import FileStorage

from utils import process_args, check_file
from predict import make_prediction

app = Flask(__name__)

api = Api(app, 
    title='API Mock integração Jacad', 
    version='1.0', 
    description='Api de integração com python flask', 
    prefix='/api'
)

upload_parser = api.parser()
upload_parser.add_argument('file', 
    location='files', 
    type=FileStorage, 
    required=True, 
    help='Arquivo que será predito pela inteligência artificial'
)

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
        responsavel por receber um arquivo no formato jpg ou pdf, o tipo do documento: cpf, rg, cnh. E responder o recebimento do arquivo
        simulando o comportamento da IA.
        Token de teste: 1234567
        
        autenticacao basic, usando o beaurus
        manda no header

        :return:
        '''

        output_message = list()
        try:
            #args = upload_parser.parse_args()
            args = self.api.payload
            uploaded_file = args['file']  # This is FileStorage instance
            type_file = args['tipo']

            output_message.append(check_file(uploaded_file, type_file))

        except:
            output_message.append({'erro': 'Arquivo não recebido'}, 400)
            return output_message


        message = process_args(args)
        output_message.append(make_prediction(message))

        for om in output_message:
            print(om)
        return output_message




if __name__ == '__main__':
    app.run("0.0.0.0", 3000, threaded=True)

