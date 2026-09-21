# FOODCORE

Полуфабрикаты для профессиональной кухни. Сайт-каталог с корзиной и оформлением заявок.

## Стек

- Python 3.14, Django 5.2 LTS
- uv, pytest, HTMX, Tailwind CSS
- SQLite (dev), PostgreSQL (prod)

## Запуск

```bash
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py runserver
```

## Тесты

```bash
uv run pytest -v
```

## Деплой

```bash
docker compose build
docker compose up -d
```
