Блог про путешествия и туризм "Yatube" 

Этот блог позволяет пользователям создать учетную запись, публиковать записи (вести личный дневник), подписываться на любимых авторов и комментировать понравившиеся записи.

Проект развёрнут на платформе "Pythonanywhere" и доступен по адресу: https://c393ox.pythonanywhere.com/

Технологии: Python 3.9.10, Django 3.2

Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:alexrashkin/hw05_final.git
```

```
cd online_store
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

* Если у вас Linux/macOS

    ```
    source env/bin/activate
    ```

* Если у вас Windows

    ```
    source env/scripts/activate
    ```

```
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```
Автор: 
- Александр Рашкин  - https://github.com/alexrashkin
