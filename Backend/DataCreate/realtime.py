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

# Servo control variables
latest_servo_command = {}
servo_mode = 'manual'  # 'manual' atau 'auto'

def set_servo_mode():
    """Set mode servo: manual atau auto"""
    global servo_mode
    data = request.get_json() or {}
    mode = data.get('mode', 'manual')  # 'manual' atau 'auto'
    
    if mode in ['manual', 'auto']:
        servo_mode = mode
        return jsonify({'status': 'success', 'mode': mode}), 200
    else:
        return jsonify({'status': 'error', 'message': 'Invalid mode'}), 400

def send_servo_command():
    """Kirim command servo manual"""
    global latest_servo_command
    data = request.get_json() or {}
    command = data.get('command')  # 'open', 'close'
    angle = data.get('angle', 90)  # Sudut servo (0-180)
    
    # Set angle berdasarkan command
    if command == 'open':
        angle = 0
    elif command == 'close':
        angle = 180
    
    latest_servo_command = {
        'command': command,
        'angle': angle,
        'mode': 'manual',
        'timestamp': datetime.now().isoformat(),
        'executed': False
    }
    
    return jsonify({'status': 'success', 'command': command, 'angle': angle}), 200

def get_servo_command():
    """Raspberry Pi ambil command servo"""
    global latest_servo_command, servo_mode
    
    if servo_mode == 'auto':
        # Generate auto command berdasarkan lux
        auto_command = generate_auto_servo_command()
        if auto_command:
            return auto_command
    
    # Return manual command jika ada
    if latest_servo_command and not latest_servo_command.get('executed'):
        latest_servo_command['executed'] = True
        return latest_servo_command
    
    return {}

def generate_auto_servo_command():
    """Generate command servo otomatis berdasarkan lux"""
    lux_data = get_latest_data_lux()
    
    if lux_data and lux_data.get('lux') is not None:
        lux = lux_data['lux']
        
        if lux > 22800:  # Terlalu terang - tutup
            command = 'close'
            angle = 180
            reason = 'Too bright'
        elif lux < 300:  # Terlalu gelap - buka
            command = 'open'
            angle = 0
            reason = 'Too dark'
        else:  # Normal - setengah
            command = 'partial'
            angle = 90
            reason = 'Normal light'
        
        return {
            'command': command,
            'angle': angle,
            'mode': 'auto',
            'reason': reason,
            'lux': lux,
            'timestamp': datetime.now().isoformat(),
            'executed': False
        }
    
    return None

def get_servo_status():
    """Get status servo dan mode"""
    return {
        'mode': servo_mode,
        'last_command': latest_servo_command,
        'timestamp': datetime.now().isoformat()
    }