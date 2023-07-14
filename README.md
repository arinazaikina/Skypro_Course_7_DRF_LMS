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
git checkout 25.2
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

## Шаг 3. Установка и настройка PostgreSQL
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

## Шаг 4. Настройка окружения
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
```
В каталоге проекта есть шаблон файла .env

## Шаг 5. Применение миграций
1. Выполнить команду
```bash
python manage.py migrate
```

## Шаг 6. Загрузка данных с помощью фикстур
1. Загрузка данных изображений
```bash
python manage.py loaddata image_data.json
```
2. Загрузка данных пользователей
```bash
python manage.py loaddata user_data.json
```
3Загрузка данных курсов и уроков
```bash
python manage.py loaddata course_data.json
```


## Шаг 7. Запуск сервера Django
1. Запустить сервер
```bash
python manage.py runserver
```
2. Перейти по адресу http://127.0.0.1:8000/swagger/
