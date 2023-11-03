import keras_ocr
from utils import  processa_str


pipeline = keras_ocr.pipeline.Pipeline()
top_left_nome = (308, 460)
bottom_right_nome = (928, 487)


top_left_cpf = (590, 700)
bottom_right_cpf = (590 + 179, 700 + 29)


top_left_cnh_numero = (795, 700)
bottom_right_cnh_numero = (795 + 141, 700 + 32)


top_left_rg = (590, 635)
bottom_right_rg = (590 + 504, 635 + 34)


def process_prediction_cnh_nome(message):
    image = message['IMAGE']

    # Crop the image
    cropped_nome = image[top_left_nome[1]:bottom_right_nome[1], top_left_nome[0]:bottom_right_nome[0]]
    # generate text predictions from the images
    prediction_nome = pipeline.recognize([cropped_nome])
    nome = ""
    for text in prediction_nome[0]:
        nome += text[0] + " "
    print(nome)
    return processa_str(nome[0:-1]), cropped_nome



def process_prediction_cnh_cpf(message):
    image = message['IMAGE']


    # Crop the image
    cropped_cpf = image[top_left_cpf[1]:bottom_right_cpf[1], top_left_cpf[0]:bottom_right_cpf[0]]
    # generate text predictions from the images
    prediction_cpf = pipeline.recognize([cropped_cpf])
    cpf = ""
    for text in prediction_cpf[0]:
        cpf += text[0] + " "
    print(cpf)
    return processa_str(cpf.replace(" ", "")), cropped_cpf



def process_prediction_cnh_numero(message):
    image = message['IMAGE']

    # Crop the image
    cropped_numero = image[top_left_cnh_numero[1]:bottom_right_cnh_numero[1], top_left_cnh_numero[0]:bottom_right_cnh_numero[0]]
    # generate text predictions from the images
    prediction_cnh_numero = pipeline.recognize([cropped_numero])
    cnh_numero = ""
    for text in prediction_cnh_numero[0]:
        cnh_numero += text[0]
    print(cnh_numero)
    return processa_str(cnh_numero.replace(" ", "")), cropped_numero



def process_prediction_cnh_rg(message):
    image = message['IMAGE']


    # Crop the image
    cropped_numero = image[top_left_rg[1]:bottom_right_rg[1],
                     top_left_rg[0]:bottom_right_rg[0]]
    # generate text predictions from the images
    prediction_rg = pipeline.recognize([cropped_numero])
    rg_numero = ""
    for text in prediction_rg[0]:
        rg_numero += text[0]
        break
    print(rg_numero)
    return processa_str(rg_numero.replace(" ", "")), cropped_numero


def process_prediction_cnh(message):
    image = message['IMAGE']

    # Crop the image
    cropped_nome = image[top_left_nome[1]:bottom_right_nome[1], top_left_nome[0]:bottom_right_nome[0]]
    # generate text predictions from the images
    prediction_nome = pipeline.recognize([cropped_nome])
    nome = ""
    for text in prediction_nome[0]:
        nome += text[0] + " "
    print(nome)
    message['DOC_NUMBER']['NOME'] = nome.upper()


    # Crop the image
    cropped_cpf = image[top_left_cpf[1]:bottom_right_cpf[1], top_left_cpf[0]:bottom_right_cpf[0]]
    # generate text predictions from the images
    prediction_cpf = pipeline.recognize([cropped_cpf])
    cpf = ""
    for text in prediction_cpf[0]:
        cpf += text[0] + " "
    print(cpf)
    message['DOC_NUMBER']['CPF'] = cpf.replace(" ", "")

    # Crop the image
    cropped_numero = image[top_left_cnh_numero[1]:bottom_right_cnh_numero[1], top_left_cnh_numero[0]:bottom_right_cnh_numero[0]]
    # generate text predictions from the images
    prediction_cnh_numero = pipeline.recognize([cropped_numero])
    cnh_numero = ""
    for text in prediction_cnh_numero[0]:
        cnh_numero += text[0]
    print(cnh_numero)
    message['DOC_NUMBER']['CNH'] = cnh_numero.replace(" ", "")



    # Crop the image
    cropped_numero = image[top_left_rg[1]:bottom_right_rg[1],
                     top_left_rg[0]:bottom_right_rg[0]]
    # generate text predictions from the images
    prediction_rg = pipeline.recognize([cropped_numero])
    rg_numero = ""
    for text in prediction_rg[0]:
        rg_numero += text[0]
        break
    print(rg_numero)
    message['DOC_NUMBER']['RG'] = rg_numero.replace(" ", "")


    return message