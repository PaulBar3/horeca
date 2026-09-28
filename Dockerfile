# FOODCORE — образ приложения для VPS (docker-compose)
FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Зависимости (все с готовыми wheels, включая psycopg2-binary под cp314)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Код проекта
COPY . .

RUN chmod +x build.sh

EXPOSE 8000

# migrate + collectstatic + superuser при первом старте → gunicorn
CMD ["bash", "-c", "bash build.sh && exec gunicorn config.wsgi:application --config gunicorn.conf.py"]
