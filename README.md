# Инструкция по запуску проекта на ОС Linux

## Шаг 1. Клонирование репозитория
1. Открыть терминал
2. С помощью команды `cd` перейти в каталог, где будет размещён проект.
3. Выполнить команду для клонирования проекта:
```bash
git clone https://github.com/arinazaikina/Skypro_Course_7_DRF_LMS.git
```
4. Перейти в каталог проекта
```bash
cd Skypro_Course_7_DRF_LMS
```
4. Переключить ветку
```bash
git checkout 26.1
```

## Шаг 2. Установка зависимостей
1. Убедиться, что в системе установлен Python3.x. 
Если нет, установить его в соответствии с инструкциями для вашей операционной системы.
2. Создать виртуальное окружение
```bash
python3 -m venv venv
```
3. Активировать виртуальное окружение
```bash
source venv/bin/activate
```
4. Установить зависимости проекта, указанные в файле `requirements.txt`
```bash
pip install -r requirements.txt
```

## Шаг 3. Установка и настройка Redis
1. Установить Redis, если он не установлен. Например, для Ubuntu выполнить следующую команду
```bash
sudo apt-get install redis-server
```
2. Запустить Redis
```bash
sudo service redis-server start
```
Это запустит Redis сервер и он будет слушать на стандартном порту 6379.

3. Убедиться, что Redis работает правильно, выполнив команду

```bash
redis-cli ping
```
Если Redis работает должным образом, в ответ придёт `PONG`.


## Шаг 4. Установка и настройка PostgreSQL
1. Установить PostreSQL, если он не установлен. 
2. Выполнить вход в интерактивную оболочку PostgreSQL от имени пользователя postgres
```bash
sudo -u postgres psql
```
3. Внутри интерактивной оболочки PostgreSQL создать базу данных с помощью следующей команды:
```commandline
CREATE DATABASE lms_db;
```
`lms_db` - название БД (можно задать другое название)
4. Закрыть интерактивную оболочку PostgreSQL
```bash
\q
```

## Шаг 5. Настройка окружения
1. В директории lms создать файл .env
```bash
touch .env
```
2. Открыть файл
```bash
nano .env
```
3. Записать в файл следующие настройки
```
DB_NAME=название_бд (lms_db)
DB_USER=имя_пользователя_бд (postgres)
DB_PASSWORD=пароь_пользователя_бд
DB_HOST=localhost
DB_PORT=5432
STRIPE_API_KEY=sk_test_....
```
В каталоге проекта есть шаблон файла .env

## Шаг 6. Применение миграций
1. Выполнить команду
```bash
python manage.py migrate
```

## Шаг 7. Загрузка данных с помощью фикстур
```bash
python manage.py loaddata data
```

## Шаг 8. Создание периодической задачи
```bash
python manage.py create_periodic_task
```

## Шаг 9. Запуск celery
1. Открыть новое окно терминала
2. Если виртуальное окружение неактивно, активировать его
```bash
source venv/bin/activate
```
3. Из каталога проекта Skypro_Course_7_DRF_LMS запустить celery
```bash
celery -A config worker --loglevel=info
```

## Шаг 10. Запуск celery-beat
1. Открыть новое окно терминала
2. Если виртуальное окружение неактивно, активировать его
```bash
source venv/bin/activate
```
3. Из каталога проекта Skypro_Course_7_DRF_LMS запустить celery
```bash
celery -A config beat --loglevel=info
```

## Шаг 11. Запуск тестов
1. Для запуска тестов выполнить команду в новом окне терминала из каталога проекта Skypro_Course_7_DRF_LMS 
```bash
coverage run --source='.' manage.py test
```
2. Для просмотра отчета о покрытии выполнить команду
```bash
coverage html && xdg-open htmlcov/index.html
```

## Шаг 12. Запуск сервера Django
1. Запустить сервер
```bash
python manage.py runserver
```
2. Перейти по адресу http://127.0.0.1:8000/swagger/

3. Полезные данные

- Админ: admin@mail.ru, пароль 0000
- Модератор: moderator@mail.com, пароль qwerty123!
- Пользователь arina@mail.com, пароль qwerty123!
- Пользователь max@mail.com, пароль qwerty123!

4. Некоторые ручки
- Для регистрации пользователя - /register/
- Для авторизации - /login/
- Подписка на курс - /course-subscriptions/ (тело запроса {"course": id_course})
- Отписка от курса - /course-unsubscribe/ (тело запроса {"course": id_course})


## Описание платежей

1. Для создания платежа использовать ручку `/payments/create`.
В теле запроса указывается ID курса, который хотим оплатить.
Платеж будет привязан к авторизованному в настоящий момент пользователю.
Платеж будет иметь статус `requires_payment_method` после создания.

2. Получить способ платежа с помощью ручки `/payments/method/create`.
В теле запроса надо указать payment_intent_id (ID намерения платежа) и токен платежа.
Strip не разрешает отправлять на сервер данные карты. Данные карты обрабатываются на frontend, а
на сервер уже отправляется токен, который генерит frontend. 
Для тестирования можно использовать следующие токены:
   - токены для успешных тестовых платежей:
        - tok_visa
        - tok_mastercard
   - токены для неуспешных тестовых платежей:
        - tok_chargeDeclined
        - tok_chargeCustomerFail
Платеж будет иметь статус `requires_confirmation`
3. Подтвердить платеж с помощью ручки `/payments/confirm/`. 
В теле запроса указывается payment_intent_id (ID намерения платежа).
Если платеж будет успешен, то статус платежа измениться на `succeeded`.
В противном случае платеж будет иметь статус `requires_confirmation`.
4. Далее в работу вступает celery.
Если celery запущено, то каждые 5 секунд будут собираться те платежи из базы данных,
у которых флаг `is_confirmed = False` и `payment_intent_id is not NULL` и `payment_method_id is not NULL`.
Для каждого платежа из этого набора celery отправить запрос на Stripe, проверит статус платежа, если он
`success`, то флаг `is_confirmed` будет изменен на `True`, платеж будет подтвержден.
