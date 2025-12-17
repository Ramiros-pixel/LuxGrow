from flask import Flask, render_template, request, jsonify
import mysql.connector
from Backend import app
from datetime import datetime, timedelta
from Backend.DataCreate.realtime import update_realtime_lux, latest_realtime_data_lux


@app.route('/')
def index():
    return "halo flask"

@app.route('/api')
def api():
    return "ini adalah api"

@app.route('/api/realtime', methods=['POST'])
def receive_realtime():
    return update_realtime_lux()

@app.route('/api/realtime', methods=['GET'])
def get_realtime():
    return jsonify(latest_realtime_data_lux())


# @app.route('/api/store', methods=['POST'])
# def store_data():
#     data = request.json
#     distance = data.get('distance')
    
#     conn = get_db_connection()
#     cur = conn.cursor()
    
#     cur.execute(
#         "INSERT INTO ultrasonik (distance) VALUES (%s)",
#         (distance,)
#     )
    
#     conn.commit()
#     cur.close()
#     conn.close()
    
#     return jsonify({'status': 'success'}), 200

# @app.route('/api/statistics', methods=['GET'])
# def get_statistics():
#     period = request.args.get('period', '24h')
    
#     if period == '1h':
#         time_delta = timedelta(hours=1)
#     elif period == '24h':
#         time_delta = timedelta(hours=24)
#     elif period == '7d':
#         time_delta = timedelta(days=7)
#     else:
#         time_delta = timedelta(hours=24)
    
#     conn = get_db_connection()
#     cur = conn.cursor(dictionary=True)
    
#     cur.execute("""
#         SELECT 
#             AVG(distance) as avg_distance,
#             MIN(distance) as min_distance,
#             MAX(distance) as max_distance,
#             COUNT(*) as total_readings
#         FROM ultrasonik
#         WHERE timestamp >= DATE_SUB(NOW(), INTERVAL %s SECOND)
#     """, (int(time_delta.total_seconds()),))
    
#     stats = cur.fetchone()
    
#     cur.execute("""
#         SELECT 
#             DATE_FORMAT(timestamp, '%Y-%m-%d %H:%i:00') as time_bucket,
#             AVG(distance) as avg_distance
#         FROM ultrasonik
#         WHERE timestamp >= DATE_SUB(NOW(), INTERVAL %s SECOND)
#         GROUP BY time_bucket
#         ORDER BY time_bucket
#     """, (int(time_delta.total_seconds()),))
    
#     history = cur.fetchall()
    
#     cur.close()
#     conn.close()
    
#     return jsonify({
#         'statistics': stats,
#         'history': history
#     })
