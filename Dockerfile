FROM python:3.10

COPY --from=openjdk:8-jre-slim /usr/local/openjdk-8 /usr/local/openjdk-8

ENV JAVA_HOME /usr/local/openjdk-8

RUN update-alternatives --install /usr/bin/java java /usr/local/openjdk-8/bin/java 1

LABEL maintainer='projeto ocr jacad'/
#RUN pacman -Syyu --noconfirm  && \
#    pacman -S --noconfirm python-3.7 python-pip python-setuptools gcc glu
ENV PYTHONUNBUFFERED 1
COPY requirements.txt /requirements.txt
WORKDIR /service




RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
RUN apt-get -y install \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-* \
    libgl1-mesa-dev;
RUN apt-get clean

RUN pip install --no-cache-dir -r /requirements.txt
COPY . /service
#CMD ["hypercorn","main:app","--worker-class","trio","--bind","0.0.0.0:8091"]
ENTRYPOINT FLASK_APP=app.py flask run --host=0.0.0.0
EXPOSE 5000