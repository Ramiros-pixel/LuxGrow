#!/usr/bin/env python3

import requests
import time
from datetime import datetime
import threading
import random

BACKEND_URL = "http://127.0.0.1:5000"
SEND_INTERVAL = 5
SERVO_CHECK_INTERVAL = 2
DHT_PIN = 4
SERVO_PIN = 18
AUTO_LUX_TOO_BRIGHT = 22800
AUTO_LUX_TOO_DARK = 300
DUMMY_MODE = True

def init_lux_sensor():
    global lux_sensor
    try:
        if not DUMMY_MODE:
            import board, busio, adafruit_tsl2591
            i2c = busio.I2C(board.SCL, board.SDA)
            lux_sensor = adafruit_tsl2591.TSL2591(i2c)
            lux_sensor.gain = adafruit_tsl2591.GAIN_LOW
            lux_sensor.integration_time = adafruit_tsl2591.INTEGRATIONTIME_100MS
            print("TSL2591 initialized")
        else:
            lux_sensor = None
            print("Lux sensor (dummy)")
    except Exception as e:
        print(f"Lux sensor error: {e}")
        lux_sensor = None

def read_lux_sensor():
    try:
        if DUMMY_MODE or lux_sensor is None:
            return round(random.uniform(100, 25000), 2)
        lux = lux_sensor.lux
        return round(lux, 2) if lux is not None and lux >= 0 else None
    except Exception as e:
        print(f"Read lux error: {e}")
        return None

def init_dht_sensor():
    global dht_sensor
    try:
        if not DUMMY_MODE:
            import board, adafruit_dht
            dht_sensor = adafruit_dht.DHT11(getattr(board, f'D{DHT_PIN}'))
            print(f"DHT11 initialized GPIO {DHT_PIN}")
        else:
            dht_sensor = None
            print("DHT11 (dummy)")
    except Exception as e:
        print(f"DHT sensor error: {e}")
        dht_sensor = None

def read_dht_sensor():
    try:
        if DUMMY_MODE or dht_sensor is None:
            return round(random.uniform(20.0, 35.0), 1), round(random.uniform(40.0, 80.0), 1)
        temp, hum = dht_sensor.temperature, dht_sensor.humidity
        if temp and hum and -40 <= temp <= 80 and 5 <= hum <= 95:
            return round(temp, 1), round(hum, 1)
        return None, None
    except RuntimeError:
        return None, None
    except Exception as e:
        print(f"Read DHT error: {e}")
        return None, None

def read_dht_with_retry(max_retries=3):
    for attempt in range(max_retries):
        temp, hum = read_dht_sensor()
        if temp and hum:
            return temp, hum
        if attempt < max_retries - 1:
            time.sleep(2)
    return None, None

class ServoController:
    def __init__(self):
        self.servo_motor = None
        self.pwm = None
        self.current_angle = 90
        try:
            if not DUMMY_MODE:
                import board, pwmio
                from adafruit_motor import servo
                self.pwm = pwmio.PWMOut(getattr(board, f'D{SERVO_PIN}'), duty_cycle=2**15, frequency=50)
                self.servo_motor = servo.Servo(self.pwm, min_pulse=500, max_pulse=2500)
                self.servo_motor.angle = self.current_angle
                print(f"Servo initialized GPIO {SERVO_PIN}")
            else:
                print("Servo (dummy)")
        except Exception as e:
            print(f"Servo error: {e}")
            self.servo_motor = None

    def move_to_angle(self, angle):
        if not 0 <= angle <= 180:
            return False
        try:
            if DUMMY_MODE or self.servo_motor is None:
                print(f"Servo (dummy): {angle} degrees")
                self.current_angle = angle
                return True
            self.servo_motor.angle = angle
            self.current_angle = angle
            print(f"Servo: {angle} degrees")
            return True
        except Exception as e:
            print(f"Servo move error: {e}")
            return False

    def cleanup(self):
        try:
            if self.pwm:
                self.pwm.deinit()
                print("Servo cleaned up")
        except Exception as e:
            print(f"Cleanup error: {e}")

class LuxGrowClient:
    def __init__(self):
        print("Initializing...")
        init_lux_sensor()
        init_dht_sensor()
        self.servo = ServoController()
        self.running = True
        print("Initialized")
        
    def send_lux_data(self, lux_value):
        try:
            data = {"lux": lux_value, "timestamp": datetime.now().isoformat()}
            response = requests.post(f"{BACKEND_URL}/api/realtime/lux", json=data, timeout=5)
            if response.status_code == 200:
                print(f"Lux sent: {lux_value}")
            else:
                print(f"Lux failed: {response.status_code}")
        except Exception as e:
            print(f"Send lux error: {e}")

    def send_dht_data(self, temperature, humidity):
        try:
            data = {"temperature": temperature, "humidity": humidity, "timestamp": datetime.now().isoformat()}
            response = requests.post(f"{BACKEND_URL}/api/realtime/dht", json=data, timeout=5)
            if response.status_code == 200:
                print(f"DHT sent: {temperature}C, {humidity}%")
            else:
                print(f"DHT failed: {response.status_code}")
        except Exception as e:
            print(f"Send DHT error: {e}")

    def check_servo_command(self):
        try:
            response = requests.get(f"{BACKEND_URL}/api/servo/command", timeout=5)
            if response.status_code == 200:
                command_data = response.json()
                if command_data:
                    command = command_data.get('command')
                    angle = command_data.get('angle', 90)
                    mode = command_data.get('mode', 'manual')
                    print(f"Servo command: {command} ({angle} degrees, {mode})")
                    self.servo.move_to_angle(angle)
                    if mode == 'auto':
                        print(f"Auto mode: {command_data.get('reason', '')} (lux: {command_data.get('lux', 0)})")
        except Exception as e:
            print(f"Check servo error: {e}")

    def sensor_loop(self):
        print("Sensor loop started")
        while self.running:
            try:
                lux = read_lux_sensor()
                temp, hum = read_dht_with_retry()
                if lux:
                    self.send_lux_data(lux)
                if temp and hum:
                    self.send_dht_data(temp, hum)
                time.sleep(SEND_INTERVAL)
            except KeyboardInterrupt:
                print("\nStopping...")
                self.running = False
                break
            except Exception as e:
                print(f"Sensor loop error: {e}")
                time.sleep(1)

    def servo_loop(self):
        print("Servo loop started")
        while self.running:
            try:
                self.check_servo_command()
                time.sleep(SERVO_CHECK_INTERVAL)
            except KeyboardInterrupt:
                self.running = False
                break
            except Exception as e:
                print(f"Servo loop error: {e}")
                time.sleep(1)

    def start(self):
        print("LuxGrow Client Starting...")
        print(f"Backend: {BACKEND_URL}")
        print(f"Interval: {SEND_INTERVAL}s")
        print(f"Mode: {'Real' if not DUMMY_MODE else 'Dummy'}")
        print("-" * 50)
        
        sensor_thread = threading.Thread(target=self.sensor_loop)
        servo_thread = threading.Thread(target=self.servo_loop)
        sensor_thread.daemon = True
        servo_thread.daemon = True
        sensor_thread.start()
        servo_thread.start()
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down...")
            self.running = False
            self.servo.cleanup()

if __name__ == "__main__":
    print("=" * 60)
    print("LuxGrow Raspberry Pi Client")
    print("=" * 60)
    try:
        response = requests.get(f"{BACKEND_URL}/api", timeout=5)
        if response.status_code == 200:
            print(f"Backend OK: {BACKEND_URL}")
        else:
            print(f"Backend status: {response.status_code}")
    except Exception as e:
        print(f"Backend error: {e}")
        print("Continuing...")
    print("-" * 60)
    client = LuxGrowClient()
    client.start()
