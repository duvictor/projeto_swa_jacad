import datetime

from flask import Flask, request
from flask_restx import Resource, Api
from werkzeug.datastructures import FileStorage

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

ALLOWED_EXTENSIONS = {'jpeg', 'pdf'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
        responavel por receber um arquivo no formato jpg ou pdf e responder o recebimento do arquivo
        :return:
        '''
        try:
            args = upload_parser.parse_args()
            uploaded_file = args['file']  # This is FileStorage instance
        except:
            return {'erro': 'Arquivo não recebido'}, 400

        if(allowed_file(uploaded_file.filename)):
            token = '1234567'
            return {'sucesso': 'Arquivo recebido com sucesso!', 'token': token}, 201
        
        return {'erro': 'Arquivo não permitido'}, 400


if __name__ == '__main__':
    app.run("0.0.0.0", 3000, threaded=True)

