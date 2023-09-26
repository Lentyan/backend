FROM python:3.11-buster

WORKDIR /app

COPY src ./src

COPY infra ./infra

COPY requirements/production.txt ./requirements.txt

RUN pip install --upgrade pip

RUN pip install -r ./requirements.txt

WORKDIR ./src

CMD ["gunicorn", "configs.wsgi:application"]
