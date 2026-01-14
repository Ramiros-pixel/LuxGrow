from flask import Flask, render_template, request, jsonify
import mysql.connector
from Backend import app
from datetime import datetime, timedelta
from Backend.DataCreate.realtime import get_latest_data_temperature, get_latest_data_lux

group_condition={}
def process_group_condition():
    def condition():


        # Fetch data once
        lux_data = get_latest_data_lux()
        lux_value = lux_data.get('lux', 0) if lux_data else 0

        # Classification Logic
        if lux_value > 0 and lux_value <= 50:
            return 'Cahaya terlalu rendah' 
        elif 50<= lux_value <= 45000:
            return 'Cahaya baik'           
        else:
            return 'Cahaya terlalu tinggi' 
        
    global group_condition
    data = request.get_json() or {}
    klasifikasi= data.get('klasifikasi', condition())
    timestamp = data.get('timestamp', datetime.now().isoformat())

    group_condition = {
        'klasifikasi': klasifikasi,
        'timestamp': timestamp
    }
    return jsonify({'status':'succes'},200)

def get_latest_data_condition():
    return group_condition