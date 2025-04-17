# Проект сайта Svoboda23
Сайт предназначен для торговли продуктами питания в учереждениях ФСИН.

Основной функционал:

    1.  Регистрация и авторизация
    2.  Ассортимент и цены изделий
    3.  Карточка товара
    4.	Корзина
    5.	Заказы
    6.	Обмен данными с 1С

Сайт написан с использованием фреймворка  [Django](https://docs.djangoproject.com/en/5.0/). Форнтенд собран на языке JavaScript, с использованием JQuery. API на базе [Django rest](https://www.django-rest-framework.org).


# Содержание

- [Установка и запуск сайта](#установка-и-запуск-сайта)
  - [Как развернуть dev-версию сайта](#как-развернуть-dev-версию-сайта)
  - [Как развернуть prod-версию сайта](#как-развернуть-prod-версию-сайта)
  - [Получение токена для пользователя (пр. admin)](#получение-токена-для-пользователя)
- [Проверить запуск сайта](#проверить-запуск-сайта)
- [Описание API проекта](#описание-api-проекта)
  - [Генерация токена по имени пользователя и паролю](#генерация-токена-по-имени-пользователя-и-паролю)
  - [Загрузка категорий из json файла](#загрузка-категорий-из-json-файла)
  - [Загрузка номенклатуры из json файла](#загрузка-номенклатуры-из-json-файла)
  - [Загрузка картинок из json файла](#загрузка-картинок-из-json-файла)
  - [Загрузка цен из json файла](#загрузка-цен-из-json-файла)
  - [Получение заказов с личного кабинета](#получение-заказов-с-личного-кабинета)
  - [Обновлени статуса заказа с 1С на сайте](обновлени-статуса-заказа-с-1с-на-сайте)
- [Подключение оплаты через Robokassa](#подключение-щплаты-через-robokassa)

# Установка и запуск сайта

Скачайте код:
```sh
git clone https://github.com/JuliaKendo/Liberty23.git
```

[Установите Python](https://www.python.org/), если этого ещё не сделали.

Проверьте, что `python` установлен и корректно настроен. Запустите его в командной строке:
```sh
python --version
```
**Важно!** Версия Python должна быть не ниже 3.9 и не выше 3.10.

Возможно, вместо команды `python` здесь и в остальных инструкциях этого README придётся использовать `python3`. Зависит это от операционной системы и от того, установлен ли у вас Python другой версии.

В каталоге проекта создайте виртуальное окружение:
```sh
python -m venv venv
```
Активируйте его. На разных операционных системах это делается разными командами:
- Windows: `.\venv\Scripts\activate`
- MacOS/Linux: `source venv/bin/activate`

Перейдите в каталог проекта:

```sh
cd Liberty23
```

## Как развернуть dev-версию сайта

Установите переменные окружения:

`SECRET_KEY` - уникальный ключ проекта.

`DEBUG` - установите 1 для разработки.

`ALLOWED_HOSTS` - см [Django docs](https://docs.djangoproject.com/en/3.1/ref/settings/#allowed-hosts).

`ALLOWED_PORT` - порт хоста, если есть

`REDIS_HOST` - адрес redis сервера, или наименование соответствующего контейнера docker

`REDIS_PORT` - порт redis

`REDIS_PWD` - пароль redis сервера

`TG_TOKEN` - токен телеграмм бота для сбора логов

`TG_CHART_ID` - id пользователя или группы телеграмм

`LOG_ENV` - вид окружения для логов (development или production)


Установите зависимости в виртуальное окружение:
```sh
pip install -r requirements.txt
```

Создайте файл базы данных SQLite и отмигрируйте её следующей командой:

```sh
python manage.py migrate
```

Запустите сервер:

```sh
python manage.py runserver
```


## Как развернуть prod-версию сайта
Установите Docker и docker compose следуя инструкциям в [документации Docker](https://docs.docker.com/engine/install/)

Установите переменные окружения:

`SECRET_KEY` - уникальный ключ проекта.

`DEBUG` - установите 0 если развертываете в prodaction или 1 в остальных случаях.

`ALLOWED_HOSTS` - см [Django docs](https://docs.djangoproject.com/en/3.1/ref/settings/#allowed-hosts).

`ALLOWED_PORT` - порт хоста, если есть

`DATABASE` - имя, используемое в sh скрипте для определения типа базы данных (пр. postgres)

`DB_ENGINE` - имя, указывает на используемый движок для доступа к БД. (пр. "django.db.backends.postgresql")

`DB_NAME` - имя базы данных

`DB_USER` - имя пользователя для доступа к базе данных

`DB_PASSWORD` - пароль пользователя для доступа к базе данных

`DB_HOST` - имя или ip адрес хоста на котором располагается база данных (в случае развертывания в docker тут пишем имя соответствующего сервиса из docker-compose)

`DB_PORT` - порт на котором развернута база данных на хосте

`REDIS_HOST` - адрес redis сервера, или наименование соответствующего контейнера docker

`REDIS_PORT` - порт redis

`REDIS_PWD` - пароль redis сервера

`TG_TOKEN` - токен телеграмм бота для сбора логов

`TG_CHART_ID`= id пользователя или группы телеграмм

`LOG_ENV` - вид окружения для логов (development или production)

Запустите развертывание сайта в Docker:

```sh
docker-compose --env-file .env.prod up -d --build
```

Выполните миргации:

```sh
docker-compose exec web python manage.py migrate --noinput
```

Выполните создание супер-пользователя:

```sh
docker-compose exec web python manage.py createsuperuser
```

Выполните сбор статики:

```sh
docker-compose exec web python manage.py collectstatic --no-input --clear
```

Получите SSL сертификаты для production:

```sh
sudo nano docker-compose.yml
```

закомментируйте строку следующую строку файла и сохраните его:

```
command: certonly --webroot --webroot-path=/var/www/certbot/ --email admin@cabinet-opt.ru --agree-tos --no-eff-email -d cabinet-opt.ru
```

```sh
sudo nano nginx/nginx.conf
```

раскомментируйте блок SSL и сохраните файл

Запустите заново сборку контейнеров

```sh
docker-compose --env-file .env.prod up -d --build
```


## Получение токена для пользователя

```sh
python manage.py drf_create_token admin
```


# Проверить запуск сайта
Откройте сайт в браузере по адресу [http://127.0.0.1:8000/](http://127.0.0.1:8000/). Если вы увидели пустую белую страницу, то не пугайтесь, выдохните и вернитесь к сборки фронтенда.


# Описание API проекта

### Генерация токена по имени пользователя и паролю

```sh
curl -X POST -H "Content-Type: application/json" -d '{"username":"username","password":"password"}' http://127.0.0.1:8000/auth-token/
```

### Загрузка категорий из json файла

```sh
curl -X POST -H "Content-Type: application/json" -d @media/products.json http://127.0.0.1:8000/catalog/upload/categories -H "Authorization: Token 0000000000000000000000000000000000000000"
```


### Загрузка номенклатуры из json файла

```sh
curl -X POST -H "Content-Type: application/json" -d @media/products.json http://127.0.0.1:8000/catalog/upload/products -H "Authorization: Token 0000000000000000000000000000000000000000"
```


### Загрузка картинок из json файла

```sh
curl -X POST -H "Content-Type: application/json" -d @media/imgs.json http://127.0.0.1:8000/catalog/upload/images -H "Authorization: Token 0000000000000000000000000000000000000000"
```


### Загрузка цен из json файла

```sh
curl -X POST -H "Content-Type: application/json" -d @media/price.json http://127.0.0.1:8000/prices/upload -H "Authorization: Token 0000000000000000000000000000000000000000"
```

### Получение заказов с сайта

```sh
curl http://127.0.0.1:8000/orders/export/2004-01-01/2012-10-19 -H "Authorization: Token 0000000000000000000000000000000000000000"
```

### Получение заказа с сайта

```sh
curl http://127.0.0.1:8000/orders/export/{order_id} -H "Authorization: Token 0000000000000000000000000000000000000000"
```

### Обновлени статуса заказа с 1С на сайте

```sh
curl http://127.0.0.1:8000/orders/import\?id\=0\&status\='' -H "Authorization: Token 0000000000000000000000000000000000000000"
```

# Подключение оплаты через Robokassa

Для подключение сервиса приема оплаты Robokassa необходимо в личном кабинете создать и активировать [магазин](https://partner.robokassa.ru/Auth/Login?ReturnUrl=%2fShops%2fEdit%2f).
В технических параметрах магазина указать следующие GET ссылки:
  - Result URL - /orders/payment/result (обработчик ответа сервиса)
  - Success URL - /catalog/products (перенаправление в случае успешной оплаты)
  - Fail URL - /orders/remove (возврат обратно к оплате заказа)

Последним шагом заполнить данные магазина в админке Django
