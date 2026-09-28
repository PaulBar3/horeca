# Деплой на облачный VPS (Docker Compose)

Прод-окружение: VPS + Docker Compose (PostgreSQL + gunicorn + Caddy с автоматическим
HTTPS). Домен — **foodbase.by**. Render (`foodcore.onrender.com`) остаётся как
обкаточная площадка с авто-деплоем при пуше в `master`.

## 1. Требования

- VPS: 2 vCPU / 2 ГБ RAM, Debian 12 или Ubuntu 24.04
- Домен `foodbase.by` зарегистрирован
- Провайдер даёт публичный IP

## 2. DNS

У регистратора/провайдера домена создать записи:

| Тип | Имя | Значение |
|-----|-----|----------|
| A | `@` | IP-адрес VPS |
| A | `www` | IP-адрес VPS |

Caddy сам получит и продлит SSL-сертификат (Let's Encrypt) — ничего настраивать
не нужно. До настройки DNS сайт доступен по `http://IP-адрес` (блок `:80`
в `docker/Caddyfile`).

## 3. Установка Docker на сервере

```bash
curl -fsSL https://get.docker.com | sh
```

## 4. Клонирование и настройка

```bash
git clone https://github.com/PaulBar3/horeca.git /opt/foodcore
cd /opt/foodcore

cp .env.example .env
# заполнить .env: DJANGO_SECRET_KEY (см. ниже), POSTGRES_PASSWORD, ADMIN_PASSWORD
```

Генерация секретного ключа:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

Минимальный обязательный набор в `.env`:

```
DJANGO_SECRET_KEY=<сгенерированный>
POSTGRES_PASSWORD=<простой пароль: латиница/цифры/_/->
ACME_EMAIL=admin@foodbase.by
```

## 5. Запуск

```bash
docker compose up -d --build
```

При первом старте: миграции → collectstatic → создание суперпользователя
(логин `admin`, пароль из `ADMIN_PASSWORD` или `admin123`) → gunicorn.

## 6. Начальные данные (один раз!)

Каталог, статьи и админ из фикстуры:

```bash
docker compose exec web python manage.py loaddata fixtures/db.json
```

**Вручную и только один раз** — повторный `loaddata` перезапишет существующие
данные продакшена.

## 7. Проверка

```bash
docker compose ps            # все сервисы healthy/up
docker compose logs -f web   # логи Django
curl -I http://<IP>          # до настройки DNS
curl -I https://foodbase.by  # после (должен быть 200 + HTTPS)
```

После первого входа — **сменить пароль** администратора в админке
(`/admin/`, Пользователи → admin).

## 8. Обновления

```bash
cd /opt/foodcore
git pull origin master
docker compose up -d --build
```

## 9. Бэкапы

```bash
# База данных
docker compose exec db pg_dump -U foodcore foodcore > backup_$(date +%F).sql

# Загруженные файлы
tar czf media_$(date +%F).tar.gz media/
```

Восстановление БД: `docker compose exec -T db psql -U foodcore foodcore < backup.sql`.

## 10. Полезные команды

```bash
docker compose logs -f caddy   # логи HTTPS/ACME
docker compose down            # остановить
docker compose restart web     # перезапустить Django
```
