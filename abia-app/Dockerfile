FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including GDAL/GEOS/PROJ for GeoDjango
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    libproj-dev \
    && rm -rf /var/lib/apt/lists/*

# Set GDAL library path for Django
ENV GDAL_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgdal.so

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "abia.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
