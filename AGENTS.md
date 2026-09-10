# FOODCORE — AGENTS.md

## Стек

- Python 3.14, Django 5.2 LTS (5.2.17)
- uv (пакетный менеджер), pytest + pytest-django + factory-boy
- python-slugify (транслитерация кириллицы → латиница)
- Tailwind CSS (CDN), HTMX (CDN)
- SQLite (dev), PostgreSQL (prod)

## Команды

```bash
uv run python manage.py runserver    # запуск сервера
uv run python manage.py createsuperuser  # создать админа
uv run python manage.py makemigrations  # миграции
uv run python manage.py migrate
uv run pytest -v                     # тесты (25 шт.)
uv run pylint --load-plugins pylint_django --django-settings-module=config.settings.development core catalog orders blog --disable=C0114,C0115,C0116,R0903,W0212,C0103,C0301,R0801  # линтер (10/10)
```

## Структура

```
config/          # settings (base/dev/prod), urls, wsgi, mixins
core/            # Главная, about, b2b, contacts, sitemap, Review
catalog/         # Category, Product, ProductImage, Packaging, TTKFile
orders/          # Корзина (сессия) + заявки: Order, OrderItem, OrderForm
blog/            # Статьи/рецепты: Article
templates/       # Шаблоны (base.html + по приложениям + партиалы)
tests/           # pytest тесты (catalog/, orders/, blog/)
```

## Модели

- `Product` → `Category` (FK), `ProductImage` (1:many), `Packaging` (1:many), `TTKFile` (1:many)
- `Order` → `OrderItem` (1:many) → `Product`, `Packaging`
- `Article` — блог
- `Review` — отзывы шеф-поваров (управление через admin)

## Корзина

- Сессия, ключ из `settings.CART_SESSION_KEY` (`foodcore_cart`)
- Формат: `{product_id: {packaging_id, quantity}}`
- HTMX POST/DELETE для add/update/remove, JSON-ответы
- Валидация: `_parse_quantity()` для safe int conversion
- Хелперы: `_resolve_cart_items()`, `_cart_total()`

## Админка

- `SlugifyAdminMixin` (`config/mixins.py`) — авто-генерация slug на английском из name/title
- JS-транслитерация (`static/admin/js/slugify.js`) — slug заполняется при вводе
- slug-поля не `prepopulated_fields` — ввод вручную или через mixin

## CBV vs FBV

- `about`, `b2b` — `TemplateView.as_view()` прямо в urls.py
- `contacts`, `trial_request` — FBV (обрабатывают POST)
- `home`, `product_list`, `product_detail`, `cart_view` — FBV

## Forms

- `orders/forms.py` — `OrderForm` (ModelForm) с виджетами и валидацией
- Валидация фильтров в `catalog/views.py` — `_apply_filters()` с проверкой допустимых значений

## Шаблоны

- Tailwind CSS через CDN (`<script src="https://cdn.tailwindcss.com">`)
- HTMX через CDN (`htmx.org@2.0.4`)
- Партиалы: `catalog/_product_card.html`, `blog/_article_card.html`
- Пагинация: `catalog/product_list.html`, `blog/article_list.html`

## Тесты

- Фикстуры в `tests/conftest.py` (client, category, product, packaging, article)
- 25 тестов: catalog (8), orders (6), blog (5)

## Запуск

```bash
uv run python manage.py createsuperuser
uv run python manage.py runserver
# http://127.0.0.1:8000 — главная
# http://127.0.0.1:8000/admin/ — админка
```
