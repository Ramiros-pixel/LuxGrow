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
SERVO_PIN = 13  # GPIO pin untuk servo
BUZZER_PIN = 17  # GPIO pin untuk buzzer

# Sensor Thresholds
AUTO_LUX_TOO_BRIGHT = 22800
AUTO_LUX_TOO_DARK = 300
LUX_HIGH_THRESHOLD = 22800  # Threshold untuk buzzer alert

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

class ServoController:
    """Continuous Servo Controller - Time-based movement"""
    def __init__(self):
        self.servo_motor = None
        self.pwm = None
        
        # Konfigurasi Gerakan (Sesuaikan dengan kebutuhan mekanik Anda)
        self.MOVEMENT_SPEED = 1.0    # 1.0 (full speed forward), -1.0 (full speed backward)
        self.STOP_SPEED = 0.0
        self.WAKTU_BUKA_PENUH = 5.0  # Detik yang dibutuhkan untuk buka penuh (SESUAIKAN)
        self.WAKTU_TUTUP_PENUH = 5.0 # Detik yang dibutuhkan untuk tutup penuh (SESUAIKAN)
        
        try:
            if not DUMMY_MODE:
                import board
                import pwmio
                from adafruit_motor import servo
                
                self.pwm = pwmio.PWMOut(getattr(board, f'D{SERVO_PIN}'), 
                                      duty_cycle=2**15, frequency=50)
                self.servo_motor = servo.ContinuousServo(self.pwm, min_pulse=500, max_pulse=2500)
                
                # Pastikan servo berhenti saat start
                self.servo_motor.throttle = self.STOP_SPEED
                print(f"✓ Continuous Servo initialized on GPIO {SERVO_PIN}")
            else:
                print("✓ Servo controller (dummy mode)")
        except Exception as e:
            print(f"✗ Error initializing servo: {e}")
            self.servo_motor = None

    def move_time(self, throttle, duration):
        """Gerakkan servo dengan kecepatan tertentu selama sekian detik"""
        try:
            if DUMMY_MODE or self.servo_motor is None:
                print(f"🔧 Servo (dummy): Running at {throttle} speed for {duration}s")
                time.sleep(duration)
                return True
            
            print(f"🔧 Servo running: speed {throttle}, duration {duration}s")
            self.servo_motor.throttle = throttle
            time.sleep(duration)
            self.servo_motor.throttle = self.STOP_SPEED
            print("🔧 Servo stopped")
            
            return True
            
        except Exception as e:
            print(f"✗ Error moving servo: {e}")
            if self.servo_motor:
                self.servo_motor.throttle = self.STOP_SPEED  # Emergency stop
            return False

    def open_shading(self):
        """Buka shading penuh (putar arah buka selama waktu tertentu)"""
        print("🌞 Opening shading...")
        # Anggap throttle positif untuk membuka (sesuaikan jika terbalik)
        return self.move_time(self.MOVEMENT_SPEED, self.WAKTU_BUKA_PENUH)

    def close_shading(self):
        """Tutup shading penuh (putar arah tutup selama waktu tertentu)"""
        print("🌙 Closing shading...")
        # Throttle negatif untuk menutup
        return self.move_time(-self.MOVEMENT_SPEED, self.WAKTU_TUTUP_PENUH)

    def partial_shading(self, percentage=50):
        """Buka shading sebagian (berdasarkan persentase waktu)"""
        # CATATAN: Pada servo 360, posisi absolut sulit diketahui tanpa sensor tambahan.
        # Fungsi ini hanya akan bergerak proporsional dari waktu penuh.
        # Asumsi: Bergerak dari posisi tertutup.
        
        waktu_gerak = (percentage / 100.0) * self.WAKTU_BUKA_PENUH
        print(f"⛅ Setting shading to ~{percentage}% (running for {waktu_gerak:.1f}s)...")
        return self.move_time(self.MOVEMENT_SPEED, waktu_gerak)

    def stop(self):
        """Hentikan motor segera"""
        if self.servo_motor:
            self.servo_motor.throttle = self.STOP_SPEED

    def cleanup(self):
        """Cleanup PWM resources"""
        try:
            if self.pwm:
                self.pwm.deinit()
                print("✓ Servo PWM cleaned up")
        except Exception as e:
            print(f"⚠️ Error during cleanup: {e}")

# ============================================================================
# BUZZER MODULE
# ============================================================================

class BuzzerController:
    """Buzzer Controller - Alert system untuk lux tinggi"""
    def __init__(self):
        self.pwm = None
        self.is_active = False
        
        try:
            if not DUMMY_MODE:
                import board
                import pwmio
                
                self.pwm = pwmio.PWMOut(getattr(board, f'D{BUZZER_PIN}'), 
                                      duty_cycle=0, frequency=2000, variable_frequency=True)
                print(f"✓ Buzzer initialized on GPIO {BUZZER_PIN}")
            else:
                print("✓ Buzzer controller (dummy mode)")
        except Exception as e:
            print(f"✗ Error initializing buzzer: {e}")
            self.pwm = None

    def play_warning_tone(self, duration=1.0):
        """Mainkan nada peringatan dengan pola beep"""
        try:
            if DUMMY_MODE or self.pwm is None:
                print(f"🔊 Buzzer (dummy): Warning tone for {duration}s")
                return True
            
            # Pattern: Beep-beep dengan frekuensi tinggi (2000 Hz)
            print(f"🔊 Buzzer: Warning tone!")
            
            # Beep pattern: 0.2s on, 0.1s off, 0.2s on
            beep_duration = 0.2
            pause_duration = 0.1
            
            # First beep
            self.pwm.duty_cycle = 32768  # 50% duty cycle
            time.sleep(beep_duration)
            
            # Pause
            self.pwm.duty_cycle = 0
            time.sleep(pause_duration)
            
            # Second beep
            self.pwm.duty_cycle = 32768
            time.sleep(beep_duration)
            
            # Stop
            self.pwm.duty_cycle = 0
            
            return True
            
        except Exception as e:
            print(f"✗ Error playing buzzer: {e}")
            if self.pwm:
                self.pwm.duty_cycle = 0
            return False

    def stop(self):
        """Hentikan buzzer"""
        if self.pwm:
            self.pwm.duty_cycle = 0

    def cleanup(self):
        """Cleanup PWM resources"""
        try:
            if self.pwm:
                self.pwm.duty_cycle = 0
                self.pwm.deinit()
                print("✓ Buzzer PWM cleaned up")
        except Exception as e:
            print(f"⚠️ Error during buzzer cleanup: {e}")

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
        self.buzzer = BuzzerController()
        
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
                    
                    # Eksekusi command servo dengan continuous servo logic
                    if command == 'open' or angle == 0:
                        self.servo.open_shading()
                    elif command == 'close' or angle == 180:
                        self.servo.close_shading()
                    else:
                        # Map angle (0-180) ke percentage (0-100)
                        percentage = (angle / 180.0) * 100
                        self.servo.partial_shading(percentage)
                    
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
                    
                    # Cek threshold dan trigger buzzer jika lux terlalu tinggi
                    if lux > LUX_HIGH_THRESHOLD:
                        print(f"⚠️ High lux detected: {lux} > {LUX_HIGH_THRESHOLD}")
                        self.buzzer.play_warning_tone(duration=1.0)
                
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
            self.buzzer.cleanup()



if __name__ == "__main__":
    print("=" * 60)
    print(" LuxGrow Raspberry Pi Client - All in One")
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
        print(" Continuing anyway...")
    
    print("-" * 60)
    
    # Start client
    client = LuxGrowClient()
    client.start()