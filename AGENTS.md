# FOODCORE — AGENTS.md

## Стек

- Python 3.14, Django 5.2 LTS (5.2.17)
- uv (пакетный менеджер), pytest + pytest-django + factory-boy
- python-slugify (транслитерация кириллицы → латиница)
- Tailwind CSS и HTMX — локально (`static/vendor/tailwindcss.js`, `static/vendor/htmx.min.js`)
- SQLite (dev), PostgreSQL (prod)

## Команды

```bash
uv run python manage.py runserver    # запуск сервера
uv run python manage.py createsuperuser  # создать админа
uv run python manage.py makemigrations  # миграции
uv run python manage.py migrate
uv run pytest -v                     # тесты (62 шт.)
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
tests/           # pytest тесты (catalog/, orders/, blog/, core/)
```

## Модели

- `Product` → `Category` (FK), `ProductImage` (1:many), `Packaging` (1:many), `TTKFile` (1:many)
- `Packaging` — `weight_kg`, `description` (необязательная подпись, напр. «≈50 шт в горсти»), `price_on_request`; видна в селекте карточки и в строке корзины
- `Order` → `OrderItem` (1:many) → `Product`, `Packaging`
- `Article` — блог
- `Review` — отзывы шеф-поваров (управление через admin)

## Корзина

- Сессия, ключ из `settings.CART_SESSION_KEY` (`foodcore_cart`)
- Формат: `{product_id: {packaging_id, quantity}}`
- HTMX POST для add/increase/decrease/remove; ответ — HTML-строки корзины + OOB-бейдж счётчика и OOB-итог (`#cart-sum`)
- Валидация: `_parse_int()`/`_parse_quantity()`; `cart_add` → 400 при неверном `product_id`/`packaging_id`
- Хелперы: `_resolve_cart_items()`, `_cart_total()`, `_price_totals()`, `_render_cart_rows()`, `_cart_rows_response()`
- Итог: `cart_sum` (Decimal|None) + `has_on_request`, партиал `orders/_cart_sum.html` (OOB в HTMX-ответах)
- Пустая корзина/форма — CSS (`#cart-items:empty`), форма в DOM всегда и не перерисовывается

## Админка

- `SlugifyAdminMixin` (`config/mixins.py`) — авто-генерация slug на английском из name/title
- JS-транслитерация (`static/admin/js/slugify.js`) — slug заполняется при вводе
- slug-поля не `prepopulated_fields` — ввод вручную или через mixin

## CBV vs FBV

- `about`, `b2b` — `TemplateView.as_view()` прямо в urls.py
- `contacts`, `trial_request` — FBV (обрабатывают POST)
- `home`, `product_list`, `product_detail`, `cart_view` — FBVщopen

## Forms

- `orders/forms.py` — `OrderForm` (ModelForm) с виджетами и валидацией
- Валидация фильтров в `catalog/views.py` — `_apply_filters()` с проверкой допустимых значений

## Шаблоны

- UI-система: шрифт Inter (`static/fonts/`), стили `.fc-input`/`.fc-btn` (`static/css/main.css`)
- Иконки: SVG-спрайт `static/icons.svg` (heroicons) + партиал `{% include "partials/_icon.html" with name="..." class="..." %}` (эмодзи заменены)
- Партиалы: `catalog/_product_card.html`, `blog/_article_card.html`, `orders/_cart_item.html`, `orders/_cart_sum.html`, `partials/_icon.html`, `partials/_pagination.html`
- Пагинация: тег `{% paginate page_obj %}` (`core/templatetags/pagination.py`) — окно ±2, сохраняет query-параметры (каталог, рецепты)
- Картинки: `Product.get_main_image()` (дружит с prefetch), `prefetch_related("images")` в списках и на главной; везде `onerror="this.remove()"` → серый плейсхолдер
- Детальная страница товара: несколько фото → сетка `grid-cols-2`; карточки/корзина — главное фото с hover-zoom

## Тесты

- Фикстуры в `tests/conftest.py` (client, category, product, packaging, article)
- 62 теста: catalog (23), orders (26), blog (9), core (4)

## Запуск

```bash
uv run python manage.py createsuperuser
uv run python manage.py runserver
# http://127.0.0.1:8000 — главная
# http://127.0.0.1:8000/admin/ — админка
```
