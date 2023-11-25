FROM python:3.12

ADD ./src /bb-bot
WORKDIR /bb-bot
RUN pip install -r requirements.txt
