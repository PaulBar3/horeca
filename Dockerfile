# FOODBASE — образ приложения для VPS (docker-compose)
FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_NO_CACHE=1 \
    UV_COMPILE_BYTECODE=1

WORKDIR /app

# uv (менеджер пакетов проекта)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Зависимости строго из uv.lock (все с готовыми wheels, включая psycopg2-binary под cp314)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
ENV PATH="/app/.venv/bin:$PATH"

# Код проекта
COPY . .

RUN chmod +x build.sh

EXPOSE 8000

# migrate + collectstatic + superuser при первом старте → gunicorn
CMD ["bash", "-c", "bash build.sh && exec gunicorn config.wsgi:application --config gunicorn.conf.py"]
