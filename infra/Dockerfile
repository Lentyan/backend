FROM python:3.11-buster

WORKDIR /app

COPY src ./src

COPY infra ./infra

COPY data ./data

COPY requirements/production.txt ./requirements.txt

RUN pip install --upgrade pip

RUN pip install -r ./requirements.txt

RUN chmod +x ./infra/backend-entrypoint

ENTRYPOINT ["./infra/backend-entrypoint"]
