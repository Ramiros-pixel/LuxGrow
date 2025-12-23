# LuxGrow Raspberry Pi Setup Guide

## Hardware Requirements
- Raspberry Pi 4 (recommended) atau Pi 3B+
- MicroSD card (16GB+)
- DHT11 Temperature & Humidity Sensor
- TSL2591 Light Sensor
- SG90 Servo Motor
- Breadboard dan jumper wires
- Power supply 5V 3A

## Wiring Diagram

### DHT11 Sensor
```
DHT11    Raspberry Pi
VCC   -> 3.3V (Pin 1)
GND   -> GND (Pin 6)
DATA  -> GPIO 4 (Pin 7)
```

### TSL2591 Light Sensor (I2C)
```
TSL2591  Raspberry Pi
VCC   -> 3.3V (Pin 1)
GND   -> GND (Pin 6)
SDA   -> SDA (Pin 3)
SCL   -> SCL (Pin 5)
```

### SG90 Servo Motor
```
Servo    Raspberry Pi
VCC   -> 5V (Pin 2)
GND   -> GND (Pin 6)
Signal-> GPIO 18 (Pin 12)
```

## Software Installation

### 1. Update Raspberry Pi OS
```bash
sudo apt update
sudo apt upgrade -y
```

### 2. Enable I2C dan GPIO
```bash
sudo raspi-config
# Pilih: Interface Options -> I2C -> Enable
# Pilih: Interface Options -> GPIO -> Enable
sudo reboot
```

### 3. Install Python Dependencies
```bash
# Install pip jika belum ada
sudo apt install python3-pip -y

# Install system dependencies
sudo apt install python3-dev python3-setuptools -y

# Install Python packages
pip3 install -r requirements.txt
```

### 4. Test Hardware
```bash
# Test I2C devices
sudo i2cdetect -y 1

# Test GPIO
gpio readall
```

## Configuration

### 1. Edit config.py
```python
# Ganti IP backend sesuai PC Anda
BACKEND_URL = "http://192.168.1.101:5000"

# Sesuaikan GPIO pins jika berbeda
DHT_PIN = 4
SERVO_PIN = 18
```

### 2. Test Individual Components
```bash
# Test DHT sensor
python3 sensor_dht.py

# Test Lux sensor
python3 sensor_lux.py

# Test Servo
python3 servo_control.py
```

## Running the Client

### 1. Manual Run
```bash
python3 main.py
```

### 2. Auto Start on Boot
```bash
# Buat service file
sudo nano /etc/systemd/system/luxgrow.service
```

Isi file service:
```ini
[Unit]
Description=LuxGrow Sensor Client
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/luxgrow
ExecStart=/usr/bin/python3 /home/pi/luxgrow/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable service:
```bash
sudo systemctl enable luxgrow.service
sudo systemctl start luxgrow.service
sudo systemctl status luxgrow.service
```

## Troubleshooting

### Common Issues

1. **I2C not working**
   ```bash
   sudo apt install i2c-tools -y
   sudo i2cdetect -y 1
   ```

2. **Permission denied for GPIO**
   ```bash
   sudo usermod -a -G gpio pi
   sudo reboot
   ```

3. **DHT sensor timeout**
   - Check wiring
   - Try different GPIO pin
   - Add pull-up resistor (4.7kΩ)

4. **Servo not moving**
   - Check power supply (5V 3A)
   - Verify GPIO pin
   - Test with multimeter

5. **Network connection issues**
   - Check WiFi connection
   - Verify backend IP address
   - Test with ping

### Logs
```bash
# View service logs
sudo journalctl -u luxgrow.service -f

# View system logs
tail -f /var/log/syslog
```

## Network Setup

### Static IP (Optional)
Edit `/etc/dhcpcd.conf`:
```
interface wlan0
static ip_address=192.168.1.100/24
static routers=192.168.1.1
static domain_name_servers=8.8.8.8
```

### WiFi Setup
Edit `/etc/wpa_supplicant/wpa_supplicant.conf`:
```
network={
    ssid="YourWiFiName"
    psk="YourWiFiPassword"
}
```

## Performance Optimization

### 1. Disable unnecessary services
```bash
sudo systemctl disable bluetooth
sudo systemctl disable cups
```

### 2. GPU memory split
Add to `/boot/config.txt`:
```
gpu_mem=16
```

### 3. Overclock (optional)
Add to `/boot/config.txt`:
```
arm_freq=1750
gpu_freq=600
```

## Monitoring

### System Status
```bash
# CPU temperature
vcgencmd measure_temp

# Memory usage
free -h

# Disk usage
df -h
```

### Service Status
```bash
sudo systemctl status luxgrow.service
```