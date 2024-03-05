FROM python:3.11.3-alpine

WORKDIR /app

ENV PIP_ROOT_USER_ACTION=ignore

RUN pip install --upgrade pip
RUN python -m venv bot-env
RUN pip install poetry

COPY . .

RUN poetry install

EXPOSE 80
CMD poetry run python src/tgbot/main.py