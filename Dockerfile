FROM python:3.7-slim-buster

ENV PYTHONDONTWRITEBYTECODE=1

ENV PYTHONUNBUFFERED=1

WORKDIR  /usr/src/app

COPY . .

RUN pip3 install -r requirements.txt

EXPOSE 8000

CMD [ "./scripts/run.sh", "--env=prod" ]
