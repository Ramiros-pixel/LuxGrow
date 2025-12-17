from flask import Flask, render_template, request, jsonify
import mysql.connector
from Backend import app
from datetime import datetime, timedelta

latest_realtime_data_lux={}
def update_realtime_lux():
    global latest_realtime_data
    data = request.get_json() or {}  
    distance = data.get('lux')
    timestamp = data.get('timestamp', datetime.now().isoformat())
    
    latest_realtime_data = {
        'distance': distance,
        'timestamp': timestamp
    }
    
    return jsonify({'status': 'success'}), 200

def get_latest_data():
    return latest_realtime_data
