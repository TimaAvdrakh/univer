FROM python:3.7-buster

ENV PYTHONUNBUFFERED 1

WORKDIR /var/app/

RUN pip install --upgrade pip wheel setuptools

COPY ./requirements.txt ./

# setting up alpine mirrors thanks to kotaktelecom
RUN echo http://mirror.yandex.ru/mirrors/alpine/v3.9/main > /etc/apk/repositories; \
    echo http://mirror.yandex.ru/mirrors/alpine/v3.9/community >> /etc/apk/repositories

RUN apk add jpeg-dev zlib-dev
RUN LIBRARY_PATH=/lib:/usr/lib

RUN apk update && \
    apk add --no-cache --virtual .build-deps \
    gcc \
    musl-dev \
    zlib-dev \
    libffi-dev\
    # python3-dev \
    linux-headers \
    postgresql-dev \
    ca-certificates \
    && pip install -r requirements.txt \
    && find /usr/local \
    \( -type d -a -name test -o -name tests \) \
    -o \( -type f -a -name '*.pyc' -o -name '*.pyo' \) \
    -exec rm -rf '{}' + \
    && runDeps="$( \
    scanelf --needed --nobanner --recursive /usr/local \
    | awk '{ gsub(/,/, "\nso:", $2); print "so:" $2 }' \
    | sort -u \
    | xargs -r apk info --installed \
    | sort -u \
    )" \
    && apk add --virtual .rundeps $runDeps \
    && apk del .build-deps

#COPY . .

EXPOSE 8000

#CMD ["python3", "/var/app/manage.py"]
