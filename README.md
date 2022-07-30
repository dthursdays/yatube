# Yatube

## Описание

Это сайт социальной сети, написанный на Python с использованием Django Framework. На сайте можно зарегестрироваться, писать посты с добавлением картинок, подписываться на интересных авторов

### Как запустить

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/dthursdays/yatube.git
```

```
cd yatube
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

```
source env/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

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

Сайт будет доступен на адресе http://127.0.0.1:8000/

## Технологии:

- python 3.9.7
- django 2.2.16

## Над проектом работал:

### Никита Сологуб
