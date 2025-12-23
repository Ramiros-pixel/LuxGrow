import time
import board
import busio
import adafruit_tsl2591

# Konfigurasi sensor lux TSL2591
try:
    i2c = busio.I2C(board.SCL, board.SDA)
    sensor = adafruit_tsl2591.TSL2591(i2c)
    
    # Set gain dan integration time
    sensor.gain = adafruit_tsl2591.GAIN_LOW  # 1x gain
    sensor.integration_time = adafruit_tsl2591.INTEGRATIONTIME_100MS
    
    print("✓ TSL2591 sensor initialized")
except Exception as e:
    print(f"✗ Error initializing TSL2591: {e}")
    sensor = None

def read_lux_sensor():
    """Baca nilai lux dari sensor TSL2591"""
    try:
        if sensor is None:
            # Fallback: return dummy data untuk testing
            import random
            return random.randint(100, 1000)
        
        # Baca lux dari sensor
        lux = sensor.lux
        
        # Validasi nilai
        if lux is not None and lux >= 0:
            return round(lux, 2)
        else:
            print("⚠️ Invalid lux reading")
            return None
            
    except Exception as e:
        print(f"✗ Error reading lux sensor: {e}")
        return None

def get_sensor_info():
    """Get informasi sensor"""
    if sensor is None:
        return {"status": "not_connected", "type": "dummy"}
    
    try:
        return {
            "status": "connected",
            "type": "TSL2591",
            "gain": sensor.gain,
            "integration_time": sensor.integration_time,
            "infrared": sensor.infrared,
            "visible": sensor.visible,
            "full_spectrum": sensor.full_spectrum
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

if __name__ == "__main__":
    # Test sensor
    print("Testing LUX sensor...")
    for i in range(10):
        lux = read_lux_sensor()
        print(f"Lux reading {i+1}: {lux}")
        time.sleep(1)
    
    print("\nSensor info:")
    print(get_sensor_info())