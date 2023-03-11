FROM python:latest

RUN apt-get update && apt-get install zip

COPY . vpnbot

WORKDIR /vpnbot

RUN pip3 install -r requirements.txt

CMD ["python3","main.py"]

