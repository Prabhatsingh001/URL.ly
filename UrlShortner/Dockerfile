FROM node:20-slim AS assets

WORKDIR /app

COPY theme/static_src/package*.json /app/theme/static_src/
RUN npm --prefix /app/theme/static_src ci

COPY . /app/
RUN npm --prefix /app/theme/static_src run build

FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /app/
COPY --from=assets /app/static/css/dist /app/static/css/dist

RUN addgroup --system django_group \
    && adduser --system --ingroup django_group django_user \
    && chown -R django_user:django_group /app

USER django_user

EXPOSE 8000

CMD ["sh", "-c", "python manage.py collectstatic --noinput && gunicorn --bind 0.0.0.0:8000 UrlShortner.wsgi:application"]
