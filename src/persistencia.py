'''
responsavel por salvar os dados para monitoria e faturamento

conectar no banco resultadoia e fazer persistencias na tabela dashboard
'''

import psycopg2
from datetime import datetime, timezone
import pytz


def conectar_banco():
    conn = psycopg2.connect(
        host="database-descomplica.c470uggfgljr.us-east-2.rds.amazonaws.com",
        database="resultadoia",
        user="postgres",
        password="Descomplica23")
    return conn


def inserir_resultado_ia(documento, valor_correto, valor_predito, campo_documento, formato, uuid_s3, metrica):
    '''
    responsavel por persistir os dados de predicao para faturamente e monitoramento do modelo
    :param documento:
    :param valor_correto:
    :param valor_predito:
    :param campo_documento:
    :param formato:
    :param uuid_s3:
    :param metrica:
    :return:
    '''
    try:

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = conectar_banco()

        # create a cursor
        cur = conn.cursor()

        # dt = datetime.now(timezone.utc)
        dt = datetime.now(pytz.timezone('America/Sao_Paulo'))

        # string_insert = "INSERT INTO dashboard(data_criacao, documento, valor_correto, valor_predito, campo_documento, formato, uuid_s3) VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(dt, documento, valor_correto, valor_predito, campo_documento, formato,uuid_s3)
        string_insert = "INSERT INTO dashboard(data_criacao, documento, valor_correto, valor_predito, campo_documento, formato, uuid_s3, metrica) VALUES ('{}', '{}' , '{}', '{}', '{}', '{}', '{}', {})".format(dt, documento, valor_correto, valor_predito, campo_documento, formato, uuid_s3, metrica)

        cur.execute(string_insert);

        conn.commit()
        cur.close()
        conn.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')



# if __name__ == '__main__':
#     inserir_resultado_ia('teste','teste','teste','teste','teste','teste', 81.10)