FROM python:3.9

WORKDIR /app

# Gerekli Python bağımlılıklarını kopyala
COPY requirements.txt .

# Bağımlılıkları yükle
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama kodunu kopyala
COPY . .

# Gerekli portu aç
EXPOSE 5000

# Uygulamayı çalıştır
CMD [ "python", "server.py" ]
