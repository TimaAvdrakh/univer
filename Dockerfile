FROM python:3.7-buster

ENV PYTHONUNBUFFERED 1

WORKDIR /var/app/

RUN pip install --upgrade pip wheel setuptools

COPY ./requirements.txt ./

COPY . .

EXPOSE 8000

CMD ["python3", "manage.py"]
