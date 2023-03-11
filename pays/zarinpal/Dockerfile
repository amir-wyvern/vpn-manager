FROM tiangolo/uwsgi-nginx-flask:latest

# COPY . app

COPY ./custom.conf /etc/nginx/conf.d/

COPY .../models.py /app/models.py

COPY .../datetimeIR.py /app/datetimeIR.py

# WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip3 install -r /app/requirements.txt

COPY ./app /app