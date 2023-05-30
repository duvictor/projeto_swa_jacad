FROM python:3.7
LABEL maintainer='projeto ocr jacad'/
#RUN pacman -Syyu --noconfirm  && \
#    pacman -S --noconfirm python-3.7 python-pip python-setuptools gcc glu
ENV PYTHONUNBUFFERED 1
COPY requirements.txt /requirements.txt
WORKDIR /service
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
RUN pip install --no-cache-dir -r /requirements.txt
COPY . /service
#CMD ["hypercorn","main:app","--worker-class","trio","--bind","0.0.0.0:8091"]
ENTRYPOINT FLASK_APP=app.py flask run --host=0.0.0.0
EXPOSE 5000