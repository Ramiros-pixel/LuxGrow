from flask import Flask, render_template, request, jsonify
import mysql.connector
from Backend import app
from datetime import datetime, timedelta
from Backend.DataCreate.realtime import get_latest_data_temperature, get_latest_data_lux

group_condition={}
def process_group_condition():
    def condition():


        if get_latest_data_lux()['lux'] > 300 and get_latest_data_lux()['lux'] < 22800:
            return 'Cahaya baik'
        elif get_latest_data_lux()['lux'] > 50:
            return 'Cahaya tidak baik'
        elif get_latest_data_lux()['lux'] > 20:
            return 'Cahaya baik'
        else:
            return 'Cahaya sangat kurang'
        
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