FROM python:3.11.3-alpine

WORKDIR /opt/urprofbot

ENV PIP_ROOT_USER_ACTION=ignore

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 80
CMD python src/tgbot/main.py