'''
responsavel por enviar dados para o bucket s3


Por exemplo, o AWS Lambda permite um milhão de solicitações gratuitas e até 3,2 milhões de segundos de tempo de computação por mês. O Amazon DynamoDB libera 25 GB de armazenamento gratuito por mês.
'''
import json
import uuid
import boto3


REGION = 'us-east-2'
ACCESS_KEY_ID = 'AKIA6ENBNSLSBWA44DNP'
SECRET_ACCESS_KEY = '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'


# PATH_IN_COMPUTER = '../requirements.txt'
BUCKET_NAME = 'descomplica-data-integration'
# KEY = 'path/in/s3/requirements.txt' # file path in S3




def publicar_json(json_dict):
    s3_resource = boto3.resource(
        's3',
        region_name=REGION,
        aws_access_key_id=ACCESS_KEY_ID,
        aws_secret_access_key=SECRET_ACCESS_KEY
    )
    data_string = json.dumps(json_dict, indent=2, default=str)
    s3_resource.Bucket(BUCKET_NAME).put_object(
        Key=str(uuid.uuid4()) + '.json',
        Body=data_string
    )



# s3_resource.Bucket(BUCKET_NAME).put_object(
#     Key=KEY,
#     Body=open(PATH_IN_COMPUTER, 'rb')
