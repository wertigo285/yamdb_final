![Yamdb_final workflow](https://github.com/wertigo285/yamdb_final/workflows/Yamdb_final/badge.svg)
# Проект "Yamdb"


Учебный проект, по разработке REST API для сервиса YaMDb — базы отзывов о фильмах, книгах и музыке, подготовленный для запуска с на базе docker.


## Установка

### 1. Установить Docker

Процесс установки описан в [официальном руководстве](https://docs.docker.com/engine/install/).

### 2. Клонировать репозиторий

```
git clone git@github.com:wertigo285/yamdb_final.git
```


## Запук проекта

Для запуска проекта в папке клонированного репозитория необходимо выполнить команду.

```
docker-compose up
```

После построения образов приложение REST API для YamDb будет развернуто в виде двух docker контейнеров:
* db  - контейнер СУБД PostgreSQL разернутый из [официального образа](https://hub.docker.com/_/postgres)
* web - контейнер веб-приложения, загруженный из образа
* nginx - контейнер с веб-серером

При запуске контейнера web автоматически выполняются миграции.

Параметры подключения веб-приложения к СУБД находятся в файле **.env** . 


## Описание API

После запуска проекта описание API доступно по адресу:
```
http://127.0.0.1:8000/redoc/
```


## Управление запущенным приложением

### Создать суперпользователя
```
docker exec -it web python manage.py createsuperuser
```

### Создать миграции
```
docker exec -it web python manage.py makemigrations
```

### Выполнить миграции
```
docker exec -it web python manage.py migrate
```

### Заполнить базу данных тестовыми данными
```
docker exec -it web python manage.py loaddata fixtures.json
```

### Остановить проект
В командной строке, в папке репозитория выполнить:
```
docker-compose down
```
### использованные технологии

* [Python 3.8](https://www.python.org/)
* [Django](https://www.djangoproject.com/)
* [Django REST framework](https://www.django-rest-framework.org/)
* [Docker](https://www.docker.com/)
* [PostgreSQL](https://www.postgresql.org/)
* [NGINX](https://nginx.org/)
