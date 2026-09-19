# ---- Base ----
FROM python:3.14-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libjpeg62-turbo-dev \
        zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# ---- Dependencies ----
FROM base AS deps

COPY pyproject.toml uv.lock ./

RUN pip install --no-cache-dir uv && \
    uv sync --frozen --no-dev --no-install-project

# ---- Build ----
FROM base AS build

COPY --from=deps /app/.venv /app/.venv

ENV PATH="/app/.venv/bin:$PATH"

COPY . .

RUN python manage.py collectstatic --noinput

# ---- Production ----
FROM base AS production

COPY --from=build /app/.venv /app/.venv
COPY --from=build /app/staticfiles /app/staticfiles

ENV PATH="/app/.venv/bin:$PATH"

COPY . .

RUN addgroup --system django && \
    adduser --system --ingroup django django && \
    chown -R django:django /app

USER django

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--config", "gunicorn.conf.py"]
