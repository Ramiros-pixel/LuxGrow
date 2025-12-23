import time
import board
import pwmio
from adafruit_motor import servo

# Konfigurasi Servo
SERVO_PIN = board.D18  # GPIO 18, ganti sesuai wiring Anda
SERVO_MIN_PULSE = 500   # Minimum pulse width (microseconds)
SERVO_MAX_PULSE = 2500  # Maximum pulse width (microseconds)

class ServoController:
    def __init__(self):
        try:
            # Initialize PWM dan servo
            self.pwm = pwmio.PWMOut(SERVO_PIN, duty_cycle=2**15, frequency=50)
            self.servo_motor = servo.Servo(
                self.pwm, 
                min_pulse=SERVO_MIN_PULSE, 
                max_pulse=SERVO_MAX_PULSE
            )
            
            # Set posisi awal ke tengah
            self.current_angle = 90
            self.servo_motor.angle = self.current_angle
            
            print(f"✓ Servo initialized on GPIO {SERVO_PIN}")
            print(f"✓ Initial position: {self.current_angle}°")
            
        except Exception as e:
            print(f"✗ Error initializing servo: {e}")
            self.servo_motor = None
            self.pwm = None

    def move_to_angle(self, angle):
        """Gerakkan servo ke sudut tertentu (0-180°)"""
        try:
            if self.servo_motor is None:
                print(f"🔧 Servo (dummy): Moving to {angle}°")
                self.current_angle = angle
                return True
            
            # Validasi sudut
            if not 0 <= angle <= 180:
                print(f"⚠️ Invalid angle: {angle}° (must be 0-180)")
                return False
            
            # Gerakkan servo secara smooth
            start_angle = self.current_angle
            step = 1 if angle > start_angle else -1
            
            for current in range(int(start_angle), int(angle) + step, step):
                self.servo_motor.angle = current
                time.sleep(0.02)  # Smooth movement
            
            self.current_angle = angle
            print(f"🔧 Servo moved to {angle}°")
            
            return True
            
        except Exception as e:
            print(f"✗ Error moving servo: {e}")
            return False

    def open_shading(self):
        """Buka shading penuh (0°)"""
        print("🌞 Opening shading...")
        return self.move_to_angle(0)

    def close_shading(self):
        """Tutup shading penuh (180°)"""
        print("🌙 Closing shading...")
        return self.move_to_angle(180)

    def partial_shading(self, percentage=50):
        """Buka shading sebagian (0-100%)"""
        angle = int((100 - percentage) * 1.8)  # Convert percentage to angle
        print(f"⛅ Setting shading to {percentage}% open...")
        return self.move_to_angle(angle)

    def get_position(self):
        """Get posisi servo saat ini"""
        return {
            "angle": self.current_angle,
            "position": self._angle_to_position(self.current_angle),
            "percentage_open": self._angle_to_percentage(self.current_angle)
        }

    def _angle_to_position(self, angle):
        """Convert angle ke posisi deskriptif"""
        if angle <= 10:
            return "fully_open"
        elif angle >= 170:
            return "fully_closed"
        else:
            return "partial"

    def _angle_to_percentage(self, angle):
        """Convert angle ke persentase terbuka"""
        return round(100 - (angle / 180 * 100), 1)

    def test_movement(self):
        """Test gerakan servo"""
        print("🧪 Testing servo movement...")
        
        positions = [
            (0, "Fully Open"),
            (45, "Quarter Closed"),
            (90, "Half Closed"),
            (135, "Three Quarter Closed"),
            (180, "Fully Closed"),
            (90, "Back to Center")
        ]
        
        for angle, description in positions:
            print(f"Moving to {angle}° ({description})")
            self.move_to_angle(angle)
            time.sleep(2)
        
        print("✓ Test completed")

    def cleanup(self):
        """Cleanup PWM resources"""
        try:
            if self.pwm:
                self.pwm.deinit()
                print("✓ Servo PWM cleaned up")
        except Exception as e:
            print(f"⚠️ Error during cleanup: {e}")

if __name__ == "__main__":
    # Test servo
    servo_controller = ServoController()
    
    try:
        # Test basic movements
        servo_controller.test_movement()
        
        # Test position info
        print("\nCurrent position:")
        print(servo_controller.get_position())
        
        # Test shading functions
        print("\nTesting shading functions...")
        servo_controller.open_shading()
        time.sleep(2)
        
        servo_controller.partial_shading(75)  # 75% open
        time.sleep(2)
        
        servo_controller.close_shading()
        time.sleep(2)
        
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted")
    finally:
        servo_controller.cleanup()