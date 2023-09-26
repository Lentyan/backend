FROM python:3.11-buster

WORKDIR /app

COPY . ./

RUN pip install --upgrade pip

RUN pip install -r ./requirements/production.txt

CMD ["gunicorn", "configs.wsgi:application"]
