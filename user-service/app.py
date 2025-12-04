# user-service/app.py

import jwt
import datetime
import sys # Loglama için gerekli
from flask import Flask, request, jsonify

app = Flask(__name__)

# ÖNEMLİ: Product-Service ile aynı anahtar olmalı
SECRET_KEY = "gizli_anahtar" 

# Basit bir kullanıcı listesi (Normalde veritabanında olur)
USERS = {"testuser": "password123"} 

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "UP", "service": "User-Service"}), 200

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Giriş Denemesi Logu
    print(f"LOG: '{username}' kullanıcısı için giriş isteği alındı.", file=sys.stdout, flush=True)

    if username in USERS and USERS[username] == password:
        # Başarılı Giriş Logu
        print(f"LOG: BAŞARILI - '{username}' için token üretiliyor.", file=sys.stdout, flush=True)

        # Token Payload (Yük) oluşturma
        payload = {
            'user_id': username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1), # 1 saat geçerli
            'iat': datetime.datetime.utcnow()
        }
        
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        return jsonify({'token': token}), 200
    
    # Başarısız Giriş Logu
    print(f"LOG: BAŞARISIZ - '{username}' için hatalı şifre veya kullanıcı adı.", file=sys.stdout, flush=True)
    return jsonify({'message': 'Invalid credentials'}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)