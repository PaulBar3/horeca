# FOODCORE

Полуфабрикаты для профессиональной кухни. Сайт-каталог с корзиной и оформлением заявок.

## Стек

- Python 3.14, Django 5.2 LTS
- uv, pytest, HTMX, Tailwind CSS (локально, без CDN)
- SQLite (dev), PostgreSQL (prod, Render — Python 3.12)

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

## Данные

Начальные данные проекта (категории, товары, фасовки, статьи, заказы, админы) — в `fixtures/db.json`. Восстановление на пустой БД (после `migrate`) или обновление существующей:

```bash
uv run python manage.py loaddata fixtures/db.json
```

Пароли админов переносятся в составе фикстуры (в хэшированном виде). Файлы `media/` (фото, PDF) в фикстуру не входят — только их пути.

## Деплой

Прод — [Render](https://foodcore.onrender.com), авто-деплой при пуше в `master`:

```bash
git push origin master
```

Сборка: `pip install -r requirements.txt` → `build.sh` (`migrate` → `collectstatic` →
superuser при отсутствии), запуск — gunicorn (`gunicorn.conf.py`), БД PostgreSQL
из `DATABASE_URL`, статика — whitenoise. Конфигурация — `render.yaml`.
