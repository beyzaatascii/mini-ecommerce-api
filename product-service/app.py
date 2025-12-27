import os
import sys 
import json
from dotenv import load_dotenv
from flask import Flask, jsonify, request
import psycopg2
from psycopg2 import extras 
import jwt
from functools import wraps
from redis import Redis

# --- PROMETHEUS KÜTÜPHANELERİ ---
from prometheus_client import start_http_server, Counter

# .env dosyasındaki değişkenleri yükle
load_dotenv() 

# Flask Uygulamasını Oluştur
app = Flask(__name__)

# ÖNEMLİ: Auth servis ile aynı olmalı
SECRET_KEY = "gizli_anahtar" 

# --- METRİK TANIMI ---
REQUEST_COUNT = Counter('http_requests_total', 'HTTP İstek Sayısı', ['method', 'endpoint', 'status'])

# ------------------ POSTGRES BAĞLANTISI ------------------
def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "db"),  # Docker host
        database=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    )
    return conn

# ------------------ REDIS BAĞLANTISI ------------------
redis_client = Redis(
    host=os.getenv("REDIS_HOST", "redis"),  # Docker host
    port=6379,
    decode_responses=True
)

# ------------------ JWT DECORATOR ------------------
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            try:
                token = request.headers['Authorization'].split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Token formatı hatalı!'}), 401
        
        if not token:
            return jsonify({'message': 'Token eksik!'}), 401

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            current_user = data['user_id']
        except Exception as e:
            return jsonify({'message': 'Token geçersiz!', 'error': str(e)}), 401

        return f(current_user, *args, **kwargs)
    return decorated

# ------------------ ENDPOINTLER ------------------

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "UP", "service": "Product-Service"}), 200


# 1. LİSTELEME (CACHE + DB)
@app.route('/products', methods=['GET'])
@token_required
def get_all_products(current_user):
    REQUEST_COUNT.labels(method='GET', endpoint='/products', status='200').inc()

    # --- REDIS CACHE KONTROLÜ ---
    cached = redis_client.get("products")

    if cached:
        print("CACHE HIT: Redis'ten veri geldi.", file=sys.stdout, flush=True)
        try:
            return jsonify(json.loads(cached))
        except Exception as e:
            print("CACHE ERROR:", e, file=sys.stdout)
            redis_client.delete("products")  # bozuk cache varsa sil değil string saklıyorsan eval OK

    # --- CACHE YOKSA DB'DEN ÇEK ---
    conn = None
    products = []
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT id, name, price, stock FROM products;")
        products = cur.fetchall()
        cur.close()

        print(f"LOG: Kullanıcı '{current_user}' listeyi DB'den çekti.", file=sys.stdout, flush=True)

        # --- REDIS'E YAZ ---
        redis_client.set("products", json.dumps(products, default=str))

    except Exception as e:
        REQUEST_COUNT.labels(method='GET', endpoint='/products', status='500').inc()
        return jsonify({"error": "Hata", "details": str(e)}), 500
    finally:
        if conn: conn.close()

    return jsonify(products)


# 2. EKLEME
@app.route('/products', methods=['POST'])
@token_required
def add_new_product(current_user):
    data = request.get_json()
    name = data.get('name')
    price = data.get('price')
    stock = data.get('stock', 0)

    if not name or not price:
        return jsonify({"message": "Eksik bilgi."}), 400

    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO products (name, price, stock) VALUES (%s, %s, %s) RETURNING id;", (name, price, stock))
        new_id = cur.fetchone()[0]
        conn.commit()
        cur.close()

        # METRİK
        REQUEST_COUNT.labels(method='POST', endpoint='/products', status='201').inc()

        # CACHE TEMİZLE
        redis_client.delete("products")

        print(f"LOG: Ürün eklendi ID: {new_id}", file=sys.stdout, flush=True)

        return jsonify({"message": "Ürün eklendi.", "id": new_id}), 201
    except Exception as e:
        REQUEST_COUNT.labels(method='POST', endpoint='/products', status='500').inc()
        return jsonify({"error": "Hata", "details": str(e)}), 500
    finally:
        if conn: conn.close()


# 3. DETAY GETİRME
@app.route('/products/<int:product_id>', methods=['GET'])
@token_required
def get_product_by_id(current_user, product_id):
    REQUEST_COUNT.labels(method='GET', endpoint='/products/id', status='200').inc()

    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT id, name, price, stock FROM products WHERE id = %s;", (product_id,))
        product = cur.fetchone()
        cur.close()

        if product is None:
            return jsonify({"message": "Bulunamadı"}), 404

        return jsonify(product), 200
    except Exception as e:
        return jsonify({"error": "Hata", "details": str(e)}), 500
    finally:
        if conn: conn.close()


# 4. GÜNCELLEME
@app.route('/products/<int:product_id>', methods=['PUT'])
@token_required
def update_product(current_user, product_id):
    data = request.get_json()
    name = data.get('name')
    price = data.get('price')
    stock = data.get('stock')

    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE products SET name = %s, price = %s, stock = %s WHERE id = %s;", (name, price, stock, product_id))

        if cur.rowcount == 0:
            conn.close()
            return jsonify({"message": "Bulunamadı"}), 404

        conn.commit()
        cur.close()

        REQUEST_COUNT.labels(method='PUT', endpoint='/products/id', status='200').inc()

        # CACHE TEMİZLE
        redis_client.delete("products")

        print(f"LOG: Ürün güncellendi ID: {product_id}", file=sys.stdout, flush=True)

        return jsonify({"message": "Güncellendi"}), 200
    except Exception as e:
        return jsonify({"error": "Hata", "details": str(e)}), 500
    finally:
        if conn: conn.close()


# 5. SİLME
@app.route('/products/<int:product_id>', methods=['DELETE'])
@token_required
def delete_product(current_user, product_id):
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM products WHERE id = %s;", (product_id,))

        if cur.rowcount == 0:
            conn.close()
            return jsonify({"message": "Bulunamadı"}), 404

        conn.commit()
        cur.close()

        REQUEST_COUNT.labels(method='DELETE', endpoint='/products/id', status='200').inc()

        # CACHE TEMİZLE
        redis_client.delete("products")

        print(f"LOG: Ürün silindi ID: {product_id}", file=sys.stdout, flush=True)

        return jsonify({"message": "Silindi"}), 200
    except Exception as e:
        return jsonify({"error": "Hata", "details": str(e)}), 500
    finally:
        if conn: conn.close()


# ------------------ UYGULAMA BAŞLATMA ------------------
if __name__ == '__main__':
    try:
        start_http_server(8000)
        print("Prometheus metrics started on port 8000", file=sys.stdout)
    except:
        print("Metrics server already running or failed", file=sys.stdout)

    app.run(host='0.0.0.0', port=5002)
