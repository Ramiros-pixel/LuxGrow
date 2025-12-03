from flask import Flask, render_template, request, jsonify
import mysql.connector
from datetime import datetime, timedelta

app = Flask(__name__,template_folder='Frontend')

DB_CONFIG = {
    'host': 'localhost',
    'database': 'db_luxgrow',
    'port': 3306,
    'user': 'root',
    'password': ''
}

latest_realtime_data = {
    'distance': None,
    'timestamp': None
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/api/realtime', methods=['POST'])
def receive_realtime():
    global latest_realtime_data
    data = request.json
    distance = data.get('distance')
    timestamp = data.get('timestamp', datetime.now().isoformat())
    
    latest_realtime_data = {
        'distance': distance,
        'timestamp': timestamp
    }
    
    return jsonify({'status': 'success'}), 200

@app.route('/api/realtime', methods=['GET'])
def get_realtime():
    return jsonify(latest_realtime_data)

@app.route('/api/store', methods=['POST'])
def store_data():
    data = request.json
    distance = data.get('distance')
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute(
        "INSERT INTO ultrasonik (distance) VALUES (%s)",
        (distance,)
    )
    
    conn.commit()
    cur.close()
    conn.close()
    
    return jsonify({'status': 'success'}), 200

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    period = request.args.get('period', '24h')
    
    if period == '1h':
        time_delta = timedelta(hours=1)
    elif period == '24h':
        time_delta = timedelta(hours=24)
    elif period == '7d':
        time_delta = timedelta(days=7)
    else:
        time_delta = timedelta(hours=24)
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    cur.execute("""
        SELECT 
            AVG(distance) as avg_distance,
            MIN(distance) as min_distance,
            MAX(distance) as max_distance,
            COUNT(*) as total_readings
        FROM ultrasonik
        WHERE timestamp >= DATE_SUB(NOW(), INTERVAL %s SECOND)
    """, (int(time_delta.total_seconds()),))
    
    stats = cur.fetchone()
    
    cur.execute("""
        SELECT 
            DATE_FORMAT(timestamp, '%Y-%m-%d %H:%i:00') as time_bucket,
            AVG(distance) as avg_distance
        FROM ultrasonik
        WHERE timestamp >= DATE_SUB(NOW(), INTERVAL %s SECOND)
        GROUP BY time_bucket
        ORDER BY time_bucket
    """, (int(time_delta.total_seconds()),))
    
    history = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return jsonify({
        'statistics': stats,
        'history': history
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)