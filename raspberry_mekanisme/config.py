# Konfigurasi LuxGrow Raspberry Pi Client

# Backend Server Configuration
BACKEND_URL = "http://192.168.1.101:5000"  # IP PC yang running Flask backend
BACKEND_TIMEOUT = 5  # Timeout untuk HTTP requests (seconds)

# Data Sending Configuration
SEND_INTERVAL = 5  # Interval kirim data sensor (seconds)
SERVO_CHECK_INTERVAL = 2  # Interval cek command servo (seconds)
MAX_RETRIES = 3  # Maximum retry untuk sensor reading

# Sensor Configuration
# DHT11 Sensor
DHT_PIN = 4  # GPIO pin untuk DHT11 (board.D4)
DHT_RETRY_DELAY = 2  # Delay between DHT retry attempts

# TSL2591 Lux Sensor (I2C)
LUX_GAIN = "LOW"  # LOW, MED, HIGH, MAX
LUX_INTEGRATION_TIME = "100MS"  # 100MS, 200MS, 300MS, 400MS, 500MS, 600MS

# Servo Configuration
SERVO_PIN = 18  # GPIO pin untuk servo (board.D18)
SERVO_MIN_PULSE = 500  # Minimum pulse width (microseconds)
SERVO_MAX_PULSE = 2500  # Maximum pulse width (microseconds)
SERVO_SMOOTH_STEP = 1  # Step size untuk smooth movement
SERVO_STEP_DELAY = 0.02  # Delay between steps (seconds)

# Auto Mode Thresholds
AUTO_LUX_TOO_BRIGHT = 22800  # Lux threshold untuk tutup shading
AUTO_LUX_TOO_DARK = 300     # Lux threshold untuk buka shading
AUTO_LUX_NORMAL_MIN = 300   # Minimum lux untuk kondisi normal
AUTO_LUX_NORMAL_MAX = 22800 # Maximum lux untuk kondisi normal

# Servo Positions
SERVO_OPEN_ANGLE = 0      # Angle untuk buka penuh
SERVO_CLOSE_ANGLE = 180   # Angle untuk tutup penuh
SERVO_PARTIAL_ANGLE = 90  # Angle untuk posisi tengah

# Logging Configuration
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_TO_FILE = False
LOG_FILE_PATH = "/home/pi/luxgrow.log"

# Network Configuration
WIFI_CHECK_INTERVAL = 30  # Check WiFi connection every 30 seconds
RECONNECT_ATTEMPTS = 5     # Max attempts to reconnect

# Error Handling
SENSOR_ERROR_THRESHOLD = 10  # Max consecutive sensor errors before alert
NETWORK_ERROR_THRESHOLD = 5  # Max consecutive network errors before alert

# Development/Testing
DUMMY_MODE = False  # Set True untuk testing tanpa hardware
DEBUG_PRINT = True  # Print debug messages