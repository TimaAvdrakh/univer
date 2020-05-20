# Работа uWSGI

Для работы в 1С:

```ini
[uwsgi]
chdir=/home/odmin/univer/univer-back
module=portal.wsgi:application
touch-reload=/home/odmin/univer/univer-back/reload
harakiri=120
processes=1
daemonize=/home/odmin/univer/univer-back/univer-1c.log
master=True
enable-threads=True
home=/home/odmin/univer/univer-back/venv
socket=/tmp/univer.sock
```

Для работы с основным проектом:
```ini
TBA
```

Запуск uwsgi идет из активной виртуалки - `. venv/bin/activate`

`uwsgi --ini production.ini --http 0.0.0.0:<свободный порт>`

Важно учитывать наличие свободного порта, т.к. на сервере еще несколько рабочих проектов, использующих uwsg
