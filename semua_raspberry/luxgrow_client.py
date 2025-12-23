#!/usr/bin/env python3
"""
LuxGrow Raspberry Pi Client - All in One File
Mengirim data sensor ke Flask backend dan menerima command servo
"""

import requests
import time
import json
from datetime import datetime
import threading
import random

# ============================================================================
# KONFIGURASI
# ============================================================================

# Backend Server Configuration
BACKEND_URL = "http://192.168.1.101:5000"  # Ganti dengan IP PC yang running Flask
SEND_INTERVAL = 5  # Kirim data setiap 5 detik
SERVO_CHECK_INTERVAL = 2  # Cek command servo setiap 2 detik

# GPIO Configuration
DHT_PIN = 4  # GPIO pin untuk DHT11
SERVO_PIN = 18  # GPIO pin untuk servo

# Sensor Thresholds
AUTO_LUX_TOO_BRIGHT = 22800
AUTO_LUX_TOO_DARK = 300

# Hardware Mode
DUMMY_MODE = True  # Set False jika pakai hardware asli

# ============================================================================
# SENSOR LUX MODULE
# ============================================================================

def init_lux_sensor():
    """Initialize TSL2591 lux sensor"""
    global lux_sensor
    try:
        if not DUMMY_MODE:
            import board
            import busio
            import adafruit_tsl2591
            
            i2c = busio.I2C(board.SCL, board.SDA)
            lux_sensor = adafruit_tsl2591.TSL2591(i2c)
            lux_sensor.gain = adafruit_tsl2591.GAIN_LOW
            lux_sensor.integration_time = adafruit_tsl2591.INTEGRATIONTIME_100MS
            print("✓ TSL2591 lux sensor initialized")
        else:
            lux_sensor = None
            print("✓ Lux sensor (dummy mode)")
    except Exception as e:
        print(f"✗ Error initializing lux sensor: {e}")
        lux_sensor = None

def read_lux_sensor():
    """Baca nilai lux dari sensor"""
    try:
        if DUMMY_MODE or lux_sensor is None:
            # Dummy data untuk testing
            return round(random.uniform(100, 25000), 2)
        
        lux = lux_sensor.lux
        if lux is not None and lux >= 0:
            return round(lux, 2)
        else:
            return None
    except Exception as e:
        print(f"✗ Error reading lux sensor: {e}")
        return None

# ============================================================================
# SENSOR DHT MODULE
# ============================================================================

def init_dht_sensor():
    """Initialize DHT11 sensor"""
    global dht_sensor
    try:
        if not DUMMY_MODE:
            import board
            import adafruit_dht
            
            dht_sensor = adafruit_dht.DHT11(getattr(board, f'D{DHT_PIN}'))
            print(f"✓ DHT11 sensor initialized on GPIO {DHT_PIN}")
        else:
            dht_sensor = None
            print("✓ DHT11 sensor (dummy mode)")
    except Exception as e:
        print(f"✗ Error initializing DHT sensor: {e}")
        dht_sensor = None

def read_dht_sensor():
    """Baca temperature dan humidity dari DHT11"""
    try:
        if DUMMY_MODE or dht_sensor is None:
            # Dummy data untuk testing
            temp = round(random.uniform(20.0, 35.0), 1)
            hum = round(random.uniform(40.0, 80.0), 1)
            return temp, hum
        
        temperature = dht_sensor.temperature
        humidity = dht_sensor.humidity
        
        if temperature is not None and humidity is not None:
            if -40 <= temperature <= 80 and 5 <= humidity <= 95:
                return round(temperature, 1), round(humidity, 1)
        
        return None, None
    except RuntimeError as e:
        if "checksum did not validate" in str(e):
            pass  # Normal DHT error
        return None, None
    except Exception as e:
        print(f"✗ Error reading DHT sensor: {e}")
        return None, None

def read_dht_with_retry(max_retries=3):
    """Baca DHT dengan retry"""
    for attempt in range(max_retries):
        temp, hum = read_dht_sensor()
        if temp is not None and hum is not None:
            return temp, hum
        if attempt < max_retries - 1:
            time.sleep(2)
    return None, None

# ============================================================================
# SERVO CONTROL MODULE
# ============================================================================

class ServoController:
    def __init__(self):
        self.current_angle = 90
        self.servo_motor = None
        self.pwm = None
        
        try:
            if not DUMMY_MODE:
                import board
                import pwmio
                from adafruit_motor import servo
                
                self.pwm = pwmio.PWMOut(getattr(board, f'D{SERVO_PIN}'), 
                                      duty_cycle=2**15, frequency=50)
                self.servo_motor = servo.Servo(self.pwm, min_pulse=500, max_pulse=2500)
                self.servo_motor.angle = self.current_angle
                print(f"✓ Servo initialized on GPIO {SERVO_PIN}")
            else:
                print("✓ Servo controller (dummy mode)")
        except Exception as e:
            print(f"✗ Error initializing servo: {e}")
            self.servo_motor = None

    def move_to_angle(self, angle):
        """Gerakkan servo ke sudut tertentu (0-180°)"""
        try:
            if not 0 <= angle <= 180:
                print(f"⚠️ Invalid angle: {angle}°")
                return False
            
            if DUMMY_MODE or self.servo_motor is None:
                print(f"🔧 Servo (dummy): Moving to {angle}°")
                self.current_angle = angle
                return True
            
            # Smooth movement
            start_angle = self.current_angle
            step = 1 if angle > start_angle else -1
            
            for current in range(int(start_angle), int(angle) + step, step):
                self.servo_motor.angle = current
                time.sleep(0.02)
            
            self.current_angle = angle
            print(f"🔧 Servo moved to {angle}°")
            return True
            
        except Exception as e:
            print(f"✗ Error moving servo: {e}")
            return False

    def cleanup(self):
        """Cleanup PWM resources"""
        try:
            if self.pwm:
                self.pwm.deinit()
                print("✓ Servo PWM cleaned up")
        except Exception as e:
            print(f"⚠️ Error during cleanup: {e}")

# ============================================================================
# MAIN CLIENT CLASS
# ============================================================================

class LuxGrowClient:
    def __init__(self):
        print("🌱 Initializing LuxGrow Client...")
        
        # Initialize sensors dan servo
        init_lux_sensor()
        init_dht_sensor()
        self.servo = ServoController()
        
        self.running = True
        print("✓ Client initialized")
        
    def send_lux_data(self, lux_value):
        """Kirim data lux ke backend"""
        try:
            data = {
                "lux": lux_value,
                "timestamp": datetime.now().isoformat()
            }
            response = requests.post(f"{BACKEND_URL}/api/realtime/lux", 
                                   json=data, timeout=5)
            if response.status_code == 200:
                print(f"✓ Lux sent: {lux_value}")
            else:
                print(f"✗ Lux failed: {response.status_code}")
        except Exception as e:
            print(f"✗ Error sending lux: {e}")

    def send_dht_data(self, temperature, humidity):
        """Kirim data DHT ke backend"""
        try:
            data = {
                "temperature": temperature,
                "humidity": humidity,
                "timestamp": datetime.now().isoformat()
            }
            response = requests.post(f"{BACKEND_URL}/api/realtime/dht", 
                                   json=data, timeout=5)
            if response.status_code == 200:
                print(f"✓ DHT sent: {temperature}°C, {humidity}%")
            else:
                print(f"✗ DHT failed: {response.status_code}")
        except Exception as e:
            print(f"✗ Error sending DHT: {e}")

    def check_servo_command(self):
        """Cek command servo dari backend"""
        try:
            response = requests.get(f"{BACKEND_URL}/api/servo/command", timeout=5)
            if response.status_code == 200:
                command_data = response.json()
                if command_data:  # Ada command baru
                    command = command_data.get('command')
                    angle = command_data.get('angle', 90)
                    mode = command_data.get('mode', 'manual')
                    
                    print(f"📡 Servo command: {command} (angle: {angle}, mode: {mode})")
                    
                    # Eksekusi command servo
                    self.servo.move_to_angle(angle)
                    
                    if mode == 'auto':
                        reason = command_data.get('reason', '')
                        lux = command_data.get('lux', 0)
                        print(f"🤖 Auto mode: {reason} (lux: {lux})")
                    
        except Exception as e:
            print(f"✗ Error checking servo command: {e}")

    def sensor_loop(self):
        """Loop utama untuk baca dan kirim data sensor"""
        print("🚀 Starting sensor data loop...")
        
        while self.running:
            try:
                # Baca sensor
                lux = read_lux_sensor()
                temp, hum = read_dht_with_retry()
                
                # Kirim ke backend
                if lux is not None:
                    self.send_lux_data(lux)
                
                if temp is not None and hum is not None:
                    self.send_dht_data(temp, hum)
                
                # Tunggu interval
                time.sleep(SEND_INTERVAL)
                
            except KeyboardInterrupt:
                print("\n🛑 Stopping sensor loop...")
                self.running = False
                break
            except Exception as e:
                print(f"✗ Error in sensor loop: {e}")
                time.sleep(1)

    def servo_loop(self):
        """Loop untuk cek command servo"""
        print("🔧 Starting servo command loop...")
        
        while self.running:
            try:
                self.check_servo_command()
                time.sleep(SERVO_CHECK_INTERVAL)
                
            except KeyboardInterrupt:
                self.running = False
                break
            except Exception as e:
                print(f"✗ Error in servo loop: {e}")
                time.sleep(1)

    def start(self):
        """Start semua thread"""
        print("🌱 LuxGrow Raspberry Pi Client Starting...")
        print(f"📡 Backend URL: {BACKEND_URL}")
        print(f"⏱️  Send interval: {SEND_INTERVAL}s")
        print(f"🔧 Servo check interval: {SERVO_CHECK_INTERVAL}s")
        print(f"🔧 Hardware mode: {'Real' if not DUMMY_MODE else 'Dummy'}")
        print("-" * 50)
        
        # Start thread untuk sensor dan servo
        sensor_thread = threading.Thread(target=self.sensor_loop)
        servo_thread = threading.Thread(target=self.servo_loop)
        
        sensor_thread.daemon = True
        servo_thread.daemon = True
        
        sensor_thread.start()
        servo_thread.start()
        
        try:
            # Keep main thread alive
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")
            self.running = False
            self.servo.cleanup()

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("🌱 LuxGrow Raspberry Pi Client - All in One")
    print("=" * 60)
    
    # Test koneksi backend
    try:
        response = requests.get(f"{BACKEND_URL}/api", timeout=5)
        if response.status_code == 200:
            print(f"✓ Backend connection OK: {BACKEND_URL}")
        else:
            print(f"⚠️ Backend responded with status: {response.status_code}")
    except Exception as e:
        print(f"✗ Cannot connect to backend: {e}")
        print("⚠️ Continuing anyway...")
    
    print("-" * 60)
    
    # Start client
    client = LuxGrowClient()
    client.start()