from keras_retinanet import models
from utils import processa_str
from src.OCR import OCR

def load_model(message):
    if message['DOC_TYPE'] == 'RG':
        return models.load_model('./models/versao3/modelo_RG.h5', backbone_name='resnet50')

    elif message['DOC_TYPE'] == 'CNH':
        return models.load_model('./models/versao3/modelo_CNH.h5', backbone_name='resnet50')

    elif message['DOC_TYPE'] == 'CPF':
        return models.load_model('./models/versao3/modelo_CPF.h5', backbone_name='resnet50')

    #elif message['DOC_TYPE'] == 'RNE':
    #    return models.load_model('./models/modelo_CNH.h5', backbone_name='resnet50')
    #
    #elif message['DOC_TYPE'] == 'PASSAPORTE':
    #    return models.load_model('./models/modelo_CNH.h5', backbone_name='resnet50')
    #
    elif message['DOC_TYPE'] == 'DIPLOMA':
        return models.load_model('./models/versao3/modelo_Diploma.h5', backbone_name='resnet50')

    elif message['DOC_TYPE'] == 'CERTIFICADO':
        return models.load_model('./models/versao3/modelo_Certidao.h5', backbone_name='resnet50')

    else:
        raise ValueError("Invalid Document Type Provided on Message")


def extract_data_from_prediction(message, dataframe):
    if dataframe['scores'].max() > 0.1:  #Deixei com 0.1 apenas para ter alguma detecção, o ideal é 0.5
        for i, row in dataframe[dataframe['scores'] == dataframe['scores'].max()].iterrows():
            if not dataframe['xmin'].empty:
                try:
                    xmin, ymin, xmax, ymax = [row['xmin'], row['ymin'], row['xmax'], row['ymax']]
                    DATA = processa_str(OCR(message, xmin,ymin,xmax,ymax))
                    return DATA
                except:
                    return ''
            else:
                return ''
    else:
        return ''

def verify_object_existence(dataframe):
    if dataframe['scores'].max() > 0.3:
        return True
    else:
        return False