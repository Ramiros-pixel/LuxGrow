from flask import Flask, render_template, request, jsonify, send_from_directory
import mysql.connector
from Backend import app
from datetime import datetime, timedelta
from Backend.DataCreate.realtime import update_realtime_lux, get_latest_data_lux,update_realtime_temperature,get_latest_data_temperature
from Backend.DataCreate.pengolahan import process_group_condition,get_latest_data_condition
from config import DB_CON

def get_db_connection():
    return mysql.connector.connect(**DB_CON)

@app.route('/')
def index():
    return send_from_directory('..', 'index.html')
@app.route('/api')
def api():
    return "ini adalah api"

@app.route('/api/realtime/lux', methods=['POST'])
def receive_realtime():
    return update_realtime_lux()


@app.route('/api/realtime/lux', methods=['GET'])
def get_realtime():
    return get_latest_data_lux()


@app.route('/api/realtime/dht', methods=['POST'])
def receive_realtime_temperature():
    return update_realtime_temperature()



@app.route('/api/realtime/dht', methods=['GET'])
def get_realtime_temperature():
    return get_latest_data_temperature()

@app.route('/api/realtime/condition', methods=['GET'])
def get_realtime_condition():
    return jsonify(get_latest_data_condition())

@app.route('/api/realtime/condition', methods=['POST'])
def post_realtime_condition():
    return process_group_condition() 

@app.route('/api/store/lux', methods=['POST'])
def store_data_lux():
    data = request.json
    lux=data.get('lux')

    conn =get_db_connection()
    cur =conn.cursor()
    cur.execute(
        "INSERT INTO lux (lux) VALUES (%s)",
        (lux,)
    )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'status':'success'}),200


@app.route('/api/store/dht', methods=['POST'])
def store_data_temperature():
    data =  request.json
    temperature=data.get('temperature')
    humidity=data.get('humidity')
    conn =get_db_connection()
    cur= conn.cursor()
    cur.execute(
        "INSERT INTO dht (temperature, humidity) VALUES (%s, %s)",
        (temperature, humidity)
    )
    conn.commit()
    cur.close()
    return jsonify({'status':'success'}),200



# |||||||||||||||||||
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
