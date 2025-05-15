FROM python:3.13-alpine 

RUN apk add --no-cache \
    zbar \
    zbar-dev \
    build-base \
    jpeg-dev \
    zlib-dev \
    libpng-dev
# Establecer el directorio de trabajo
WORKDIR /app
# Copiar requirements.txt e instalar dependencias
COPY requirements.txt .
RUN pip install --default-timeout=100 --no-cache-dir -r requirements.txt
# Copiar el resto del código
COPY . .
EXPOSE 8083
CMD [ "python", "run.py" ]
#CMD sh -c "gunicorn --bind 0.0.0.0:8081 --workers 4 --forwarded-allow-ips=*  wsgi:app"