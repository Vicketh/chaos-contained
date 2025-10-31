FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . /app

RUN python manage.py collectstatic --noinput || true

EXPOSE 8000
CMD ["gunicorn", "chaos_api.wsgi:application", "--bind", "0.0.0.0:8000"]

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# system deps
RUN apt-get update && apt-get install -y build-essential libpq-dev curl && rm -rf /var/lib/apt/lists/*

# copy
COPY backend/requirements.txt /app/requirements.txt

# install deps
RUN pip install --upgrade pip
RUN pip install -r /app/requirements.txt

# copy project
COPY backend/ /app/

ENV DJANGO_SETTINGS_MODULE=chaos_api.settings

# collect static (if any)
RUN python manage.py collectstatic --noinput || true

CMD ["gunicorn", "chaos_api.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
