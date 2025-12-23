# LuxGrow Single File Setup

## Quick Start

### 1. Copy ke Raspberry Pi
```bash
# Copy file luxgrow_client.py ke Raspberry Pi
scp luxgrow_client.py pi@192.168.1.100:/home/pi/
```

### 2. Install Dependencies
```bash
# Di Raspberry Pi
pip3 install requests

# Jika pakai hardware asli, uncomment di requirements.txt dan install
# pip3 install -r requirements.txt
```

### 3. Edit Konfigurasi
```bash
nano luxgrow_client.py
```

Edit bagian konfigurasi:
```python
# Ganti IP dengan PC yang running Flask
BACKEND_URL = "http://192.168.1.101:5000"

# Set False jika pakai hardware asli
DUMMY_MODE = True  # True = testing, False = hardware asli

# GPIO pins (sesuaikan dengan wiring)
DHT_PIN = 4
SERVO_PIN = 18
```

### 4. Jalankan
```bash
python3 luxgrow_client.py
```

### 5. Auto Start (Optional)
```bash
# Buat service
sudo nano /etc/systemd/system/luxgrow.service
```

Isi service:
```ini
[Unit]
Description=LuxGrow Client
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi
ExecStart=/usr/bin/python3 /home/pi/luxgrow_client.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable service:
```bash
sudo systemctl enable luxgrow.service
sudo systemctl start luxgrow.service
```

## Features

- **Single file** - Semua kode dalam 1 file
- **Dummy mode** - Testing tanpa hardware
- **Auto retry** - Sensor error handling
- **Multi-threading** - Sensor dan servo parallel
- **Error handling** - Robust error management

## Hardware Wiring

### DHT11
- VCC → 3.3V
- GND → GND  
- DATA → GPIO 4

### TSL2591 (I2C)
- VCC → 3.3V
- GND → GND
- SDA → GPIO 2
- SCL → GPIO 3

### Servo
- VCC → 5V
- GND → GND
- Signal → GPIO 18

## Troubleshooting

### Test koneksi backend
```bash
curl http://192.168.1.101:5000/api
```

### Check logs
```bash
sudo journalctl -u luxgrow.service -f
```