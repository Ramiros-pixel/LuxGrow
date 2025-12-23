import requests
import time
import json
from datetime import datetime
import threading
from sensor_lux import read_lux_sensor
from sensor_dht import read_dht_sensor
from servo_control import ServoController

# Konfigurasi Backend Server
BACKEND_URL = "http://192.168.1.101:5000"  # Ganti dengan IP PC yang running Flask
SEND_INTERVAL = 5  # Kirim data setiap 5 detik
SERVO_CHECK_INTERVAL = 2  # Cek command servo setiap 2 detik

class LuxGrowClient:
    def __init__(self):
        self.servo = ServoController()
        self.running = True
        
    def send_lux_data(self, lux_value):
        """Kirim data lux ke backend"""
        try:
            data = {
                "lux": lux_value,
                "timestamp": datetime.now().isoformat()
            }
            response = requests.post(f"{BACKEND_URL}/api/realtime/lux", json=data, timeout=5)
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
            response = requests.post(f"{BACKEND_URL}/api/realtime/dht", json=data, timeout=5)
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
                temp, hum = read_dht_sensor()
                
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

if __name__ == "__main__":
    client = LuxGrowClient()
    client.start()