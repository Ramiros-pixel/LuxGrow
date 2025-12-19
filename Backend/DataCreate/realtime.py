from flask import Flask, render_template, request, jsonify
import mysql.connector
from Backend import app
from datetime import datetime, timedelta

latest_realtime_data_lux={}
def update_realtime_lux():
    global latest_realtime_data_lux
    data = request.get_json() or {}  
    lux = data.get('lux')
    timestamp = data.get('timestamp', datetime.now().isoformat())
    
    latest_realtime_data_lux = {
        'lux': lux,
        'timestamp': timestamp
    }
    
    return jsonify({'status': 'success'}), 200

def get_latest_data_lux():
    return latest_realtime_data_lux

latest_temperature={}
def update_realtime_temperature():
    global latest_temperature
    data = request.get_json() or {}
    temperature = data.get('temperature')
    humidity= data.get('humidity')
    timestamp = data.get('timestamp', datetime.now().isoformat())

    latest_temperature = {
        'temperature': temperature,
        'humidity': humidity,
        'timestamp': timestamp
    }

    return jsonify({'status': 'success'}), 200

def get_latest_data_temperature():
    return latest_temperature
