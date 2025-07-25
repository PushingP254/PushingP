
from flask import Flask, request, jsonify, send_from_directory
from datetime import datetime, timedelta
import json
import os

app = Flask(__name__)
users_db = "users.json"

# Load or create user DB
if not os.path.exists(users_db):
    with open(users_db, "w") as f:
        json.dump({}, f)

def load_users():
    with open(users_db) as f:
        return json.load(f)

def save_users(users):
    with open(users_db, "w") as f:
        json.dump(users, f)

def expire_users():
    users = load_users()
    now = datetime.now()
    for mac in list(users):
        if datetime.fromisoformat(users[mac]['expiry']) < now:
            del users[mac]
    save_users(users)

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/pay', methods=['POST'])
def pay():
    data = request.json
    mac = data.get('mac')
    amount = int(data.get('amount'))
    now = datetime.now()

    duration_map = {
        5: timedelta(hours=1),
        10: timedelta(hours=3),
        20: timedelta(hours=12),
        150: timedelta(days=7),
        280: timedelta(days=14),
        500: timedelta(days=30)
    }

    if amount not in duration_map:
        return jsonify({'status': 'error', 'message': 'Invalid package'})

    expiry = now + duration_map[amount]
    users = load_users()
    users[mac] = {'expiry': expiry.isoformat()}
    save_users(users)

    # Simulated STK Push
    return jsonify({'status': 'success', 'message': f'STK Push sent for Ksh. {amount}', 'expires_at': expiry.isoformat()})

@app.route('/check', methods=['GET'])
def check():
    mac = request.args.get('mac')
    users = load_users()
    expire_users()
    if mac in users:
        return jsonify({'access': True, 'expiry': users[mac]['expiry']})
    return jsonify({'access': False})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
