import time
import board
import adafruit_dht

# Konfigurasi DHT11 sensor
DHT_PIN = board.D4  # GPIO 4, ganti sesuai wiring Anda

try:
    dht = adafruit_dht.DHT11(DHT_PIN)
    print("✓ DHT11 sensor initialized on GPIO 4")
except Exception as e:
    print(f"✗ Error initializing DHT11: {e}")
    dht = None

def read_dht_sensor():
    """Baca temperature dan humidity dari DHT11"""
    try:
        if dht is None:
            # Fallback: return dummy data untuk testing
            import random
            temp = round(random.uniform(20.0, 35.0), 1)
            hum = round(random.uniform(40.0, 80.0), 1)
            return temp, hum
        
        # Baca dari sensor DHT11
        temperature = dht.temperature
        humidity = dht.humidity
        
        # Validasi nilai
        if temperature is not None and humidity is not None:
            # DHT11 range: temp -40 to 80°C, humidity 5-95%
            if -40 <= temperature <= 80 and 5 <= humidity <= 95:
                return round(temperature, 1), round(humidity, 1)
            else:
                print(f"⚠️ Invalid DHT reading: {temperature}°C, {humidity}%")
                return None, None
        else:
            print("⚠️ DHT sensor returned None values")
            return None, None
            
    except RuntimeError as e:
        # DHT sensor sering error, ini normal
        if "checksum did not validate" in str(e):
            print("⚠️ DHT checksum error (normal, will retry)")
        else:
            print(f"⚠️ DHT runtime error: {e}")
        return None, None
    except Exception as e:
        print(f"✗ Error reading DHT sensor: {e}")
        return None, None

def read_dht_with_retry(max_retries=3):
    """Baca DHT dengan retry karena sensor sering error"""
    for attempt in range(max_retries):
        temp, hum = read_dht_sensor()
        if temp is not None and hum is not None:
            return temp, hum
        
        if attempt < max_retries - 1:
            time.sleep(2)  # Wait before retry
    
    print(f"✗ Failed to read DHT after {max_retries} attempts")
    return None, None

def get_dht_info():
    """Get informasi DHT sensor"""
    if dht is None:
        return {"status": "not_connected", "type": "dummy", "pin": "N/A"}
    
    return {
        "status": "connected",
        "type": "DHT11",
        "pin": str(DHT_PIN),
        "temperature_range": "-40 to 80°C",
        "humidity_range": "5 to 95%"
    }

if __name__ == "__main__":
    # Test sensor
    print("Testing DHT11 sensor...")
    print(f"Pin: {DHT_PIN}")
    print("-" * 30)
    
    for i in range(10):
        temp, hum = read_dht_with_retry()
        if temp is not None and hum is not None:
            print(f"Reading {i+1}: {temp}°C, {hum}%")
        else:
            print(f"Reading {i+1}: Failed")
        time.sleep(3)  # DHT11 needs 2s between readings
    
    print("\nSensor info:")
    print(get_dht_info())