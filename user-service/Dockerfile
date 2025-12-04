# user-service/Dockerfile

FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    musl-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*
# Çalışma dizinini ayarla
WORKDIR /usr/src/app

# Bağımlılıkları kopyala ve kur (Flask ve PyJWT)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama kodunu kopyala
COPY . .

# Uygulamanın çalışacağı portu belirle (5001)
EXPOSE 5001

# Uygulamayı başlat
CMD ["python", "app.py"]