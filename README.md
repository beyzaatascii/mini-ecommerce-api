# 🚀 E-TİCARET MİKROSERVİS API PROJESİ (Flask & Docker)

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg?style=for-the-badge&logo=python)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.x-lightgrey?style=for-the-badge&logo=flask)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/Docker-20.10+-blue?style=for-the-badge&logo=docker)](https://www.docker.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13-blue?style=for-the-badge&logo=postgresql)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-6.x-red?style=for-the-badge&logo=redis)](https://redis.io/)
[![Prometheus](https://img.shields.io/badge/Prometheus-2.x-orange?style=for-the-badge&logo=prometheus)](https://prometheus.io/)
[![Grafana](https://img.shields.io/badge/Grafana-9.x-orange?style=for-the-badge&logo=grafana)](https://grafana.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

## 🌟 Proje Hakkında

Bu proje, modern bir e-ticaret uygulamasının arka plan (backend) sistemini mikroservis mimarisiyle geliştirmektedir. Sistem; kullanıcı yönetimi, ürün kataloglama, JWT tabanlı kimlik doğrulama, Redis ile önbellekleme ve uçtan uca izlenebilirlik (monitoring) özelliklerini barındırır. Tüm servisler Docker konteynerleri üzerinde izole edilmiş ve AWS EC2 bulut platformunda dağıtılmıştır.

### Temel Özellikler
- **Mikroservis Mimarisi:** User Service ve Product Service olmak üzere iki bağımsız servis.
- **RESTful API:** HTTP protokolü üzerinden JSON formatında haberleşme.
- **Güvenlik:** JWT (JSON Web Token) tabanlı kimlik doğrulama ve yetkilendirme.
- **Veri Kalıcılığı:** PostgreSQL ile ilişkisel veri yönetimi.
- **Performans Optimizasyonu:** Redis ile hızlı veri önbellekleme.
- **API Gateway:** Nginx ile tek giriş noktası ve yük dengeleme.
- **İzlenebilirlik (Observability):** Prometheus (metrik toplama) ve Grafana (veri görselleştirme) entegrasyonu.
- **Log Yönetimi:** Dozzle ile merkezi konteyner log takibi.
- **Konteynerizasyon:** Docker ve Docker Compose ile kolay dağıtım ve orkestrasyon.
- **Bulut Dağıtımı:** AWS EC2 üzerinde canlı yayın.

## 🚀 Canlı Ortam Bilgileri (AWS EC2)

Proje, AWS EC2 üzerinde **13.62.50.248** IP adresi üzerinden canlı olarak erişilebilir durumdadır.

| Servis Adı | Erişim Linki | Açıklama |
| :--- | :--- | :--- |
| **API Gateway (Ana Giriş)** | `http://13.62.50.248/` | Tüm API isteklerinin ana giriş noktası (Port 80) |
| **Grafana Dashboard** | `http://13.62.50.248:3000` | Sistem metriklerinin görselleştirildiği izleme paneli (Giriş: `admin/admin`) |
| **Dozzle Log Viewer** | `http://13.62.50.248:8080` | Tüm konteynerlerin canlı log kayıtlarını görüntüleme |
| **Prometheus Metrikleri** | `http://13.62.50.248:9090/targets` | Prometheus'un topladığı ham metrik verileri ve servislerin durumu |
| **Doğrudan Ürün Servisi** | `http://13.62.50.248:5002/products` | Ürünleri doğrudan listelemek için (API Gateway'siz) |

## 🛠️ Yerel Kurulum ve Çalıştırma

Bu projeyi yerel makinenizde (Ubuntu, macOS veya Windows WSL2) çalıştırmak için aşağıdaki adımları izleyin.

### Ön Koşullar
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) kurulu olmalı (Docker Compose ile birlikte gelir).
- `git` kurulu olmalı.

### Adımlar
1.  **Depoyu Klonlayın:**
    ```bash
    git clone [https://github.com/beyzaatascii/mini-ecommerce-api.git](https://github.com/beyzaatascii/mini-ecommerce-api.git)
    cd mini-ecommerce-api
    ```

2.  **Sistemi Ayağa Kaldırın:**
    Tüm mikroservisleri, veritabanını ve izleme araçlarını başlatmak için:
    ```bash
    sudo docker-compose up --build -d
    ```
    *(Windows'ta `sudo` kullanmanıza gerek olmayabilir.)*

3.  **Veritabanını İlklendirin:**
    PostgreSQL içinde `products` tablosunu oluşturmak için:
    ```bash
    sudo docker exec -it postgres_db psql -U ecomuser -d ecomdb -c "CREATE TABLE products (id SERIAL PRIMARY KEY, name VARCHAR(100), price DECIMAL, stock INTEGER);"
    ```

4.  **Servislerin Durumunu Kontrol Edin:**
    ```bash
    sudo docker ps
    ```
    Tüm servislerin `Up` durumda olduğunu görmelisiniz.

## 🧪 API Testleri (Postman / cURL)

API Gateway'e (Port 80) istek atarak sistemi test edebilirsiniz.

### 1. Kullanıcı Girişi (Login) ve JWT Token Alma
- **Endpoint:** `POST http://localhost/users/login`
- **Body:** `{"username": "testuser", "password": "password"}`
- **Yanıt:** JWT `access_token` döner. Bu token'ı sonraki isteklerde `Authorization: Bearer <token>` başlığıyla kullanın.

### 2. Yeni Ürün Ekleme
- **Endpoint:** `POST http://localhost/products`
- **Headers:** `Authorization: Bearer <JWT_TOKEN>`
- **Body:** `{"name": "Yeni Gaming Klavye", "price": 1200.00, "stock": 50}`
- **Yanıt:** `201 Created` ve eklenen ürünün detayları.

### 3. Tüm Ürünleri Listeleme
- **Endpoint:** `GET http://localhost/products`
- **Yanıt:** Tüm ürünlerin JSON formatında listesi.

## 📈 İzleme ve Log Yönetimi

Yerel olarak başlattığınızda da aynı arayüzlere `localhost` üzerinden erişebilirsiniz:

- **Grafana:** `http://localhost:3000`
- **Dozzle Log Viewer:** `http://localhost:8080`
- **Prometheus:** `http://localhost:9090`

## 🤝 Katkıda Bulunma

Geliştirmelere açığız! Her türlü katkı, hata bildirimi veya özellik önerisi memnuniyetle karşılanır. Lütfen bir Pull Request göndermeden önce mevcut sorunlara göz atın.


---
