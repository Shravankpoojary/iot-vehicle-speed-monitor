"""
============================================================
  Speed Monitoring System — Raspberry Pi
  Hardware : 2x IR Break-Beam Sensors + Raspberry Pi
  Platform : ThingSpeak IoT Dashboard
  Author   : Your Name
  Date     : 2025
============================================================

WIRING DIAGRAM:
─────────────────────────────────────────────────
  IR Sensor 1 (START gate)
    VCC  → Pin 2  (5V)
    GND  → Pin 6  (GND)
    OUT  → GPIO17 (Pin 11)

  IR Sensor 2 (END gate)
    VCC  → Pin 4  (5V)
    GND  → Pin 9  (GND)
    OUT  → GPIO27 (Pin 13)

  NOTE: IR break-beam sensors output HIGH normally,
        and go LOW when beam is broken (object detected)
─────────────────────────────────────────────────

ThingSpeak Channel Fields:
  Field 1 → Speed (km/h)
  Field 2 → Time taken (ms)
  Field 3 → Status (FAST / NORMAL / SLOW)
"""

import RPi.GPIO as GPIO
import time
import requests
import datetime

# ─────────────────────────────────────────────
#  CONFIGURATION — Edit these values
# ─────────────────────────────────────────────

# GPIO Pin Numbers (BCM mode)
SENSOR_1_PIN = 17       # First IR sensor  (START gate)
SENSOR_2_PIN = 27       # Second IR sensor (END gate)

# Distance between the two sensors in METERS
# Measure this carefully with a ruler!
DISTANCE_METERS = 0.20  # 20 cm = 0.20 m (adjust to your setup)

# ThingSpeak Configuration
THINGSPEAK_WRITE_KEY = "YOUR_WRITE_API_KEY"   # ← Replace with your Write API Key
THINGSPEAK_URL       = "https://api.thingspeak.com/update"

# Speed thresholds for status classification
SPEED_FAST   = 10.0    # km/h — above this = FAST
SPEED_SLOW   = 2.0     # km/h — below this = SLOW

# Minimum time between uploads to ThingSpeak (seconds)
# ThingSpeak free tier minimum = 15 seconds
UPLOAD_COOLDOWN = 15

# Debounce time in seconds (ignore re-triggers within this window)
DEBOUNCE_TIME = 0.05    # 50 ms

# ─────────────────────────────────────────────
#  GLOBAL STATE
# ─────────────────────────────────────────────
sensor1_trigger_time = None   # Timestamp when sensor 1 was triggered
last_upload_time     = 0      # Timestamp of last ThingSpeak upload
measurement_active   = False  # Whether we're waiting for sensor 2


# ─────────────────────────────────────────────
#  GPIO SETUP
# ─────────────────────────────────────────────
def setup_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    # Both sensors as inputs with pull-up resistors
    # Pull-up means pin reads HIGH normally, LOW when beam broken
    GPIO.setup(SENSOR_1_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(SENSOR_2_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    print("[GPIO] Pins configured successfully")
    print(f"[GPIO] Sensor 1 → GPIO{SENSOR_1_PIN}")
    print(f"[GPIO] Sensor 2 → GPIO{SENSOR_2_PIN}")


# ─────────────────────────────────────────────
#  SPEED CALCULATION
# ─────────────────────────────────────────────
def calculate_speed(time_seconds):
    """
    Speed = Distance / Time
    Convert m/s → km/h by multiplying by 3.6
    """
    if time_seconds <= 0:
        return 0.0
    speed_ms  = DISTANCE_METERS / time_seconds   # meters per second
    speed_kmh = speed_ms * 3.6                   # km/h
    return round(speed_kmh, 2)


# ─────────────────────────────────────────────
#  STATUS CLASSIFICATION
# ─────────────────────────────────────────────
def classify_speed(speed_kmh):
    if speed_kmh >= SPEED_FAST:
        return "FAST"
    elif speed_kmh <= SPEED_SLOW:
        return "SLOW"
    else:
        return "NORMAL"


# ─────────────────────────────────────────────
#  UPLOAD TO THINGSPEAK
# ─────────────────────────────────────────────
def upload_to_thingspeak(speed_kmh, time_ms, status):
    global last_upload_time

    current_time = time.time()

    # Enforce ThingSpeak rate limit
    if current_time - last_upload_time < UPLOAD_COOLDOWN:
        remaining = UPLOAD_COOLDOWN - (current_time - last_upload_time)
        print(f"[ThingSpeak] Rate limit — skipping upload (retry in {remaining:.1f}s)")
        return False

    try:
        payload = {
            "api_key" : THINGSPEAK_WRITE_KEY,
            "field1"  : speed_kmh,     # Speed in km/h
            "field2"  : time_ms,       # Time taken in ms
            "field3"  : status,        # FAST / NORMAL / SLOW
        }

        response = requests.post(
            THINGSPEAK_URL,
            params=payload,
            timeout=10
        )

        if response.status_code == 200 and response.text != "0":
            last_upload_time = current_time
            print(f"[ThingSpeak] ✓ Data uploaded! Entry ID: {response.text.strip()}")
            return True
        else:
            print(f"[ThingSpeak] ✗ Upload failed. Response: {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print("[ThingSpeak] ✗ No internet connection!")
        return False
    except requests.exceptions.Timeout:
        print("[ThingSpeak] ✗ Request timed out!")
        return False
    except Exception as e:
        print(f"[ThingSpeak] ✗ Unexpected error: {e}")
        return False


# ─────────────────────────────────────────────
#  SENSOR 1 CALLBACK — Object enters gate
# ─────────────────────────────────────────────
def sensor1_triggered(channel):
    global sensor1_trigger_time, measurement_active

    # Debounce check
    current_time = time.time()
    if measurement_active:
        return  # Already measuring, ignore re-trigger

    # Record start time
    sensor1_trigger_time = current_time
    measurement_active   = True

    timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"\n[Sensor 1] ⚡ Object detected at {timestamp}")
    print(f"[Sensor 1] Timing started — waiting for Sensor 2...")


# ─────────────────────────────────────────────
#  SENSOR 2 CALLBACK — Object exits gate
# ─────────────────────────────────────────────
def sensor2_triggered(channel):
    global sensor1_trigger_time, measurement_active

    if not measurement_active or sensor1_trigger_time is None:
        print("[Sensor 2] ⚠ Triggered but no start time recorded. Ignoring.")
        return

    # Calculate elapsed time
    end_time     = time.time()
    elapsed_sec  = end_time - sensor1_trigger_time
    elapsed_ms   = round(elapsed_sec * 1000, 2)

    # Reset state
    measurement_active   = False
    sensor1_trigger_time = None

    # Calculate speed
    speed_kmh = calculate_speed(elapsed_sec)
    status    = classify_speed(speed_kmh)

    # Print results
    timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[Sensor 2] ⚡ Object detected at {timestamp}")
    print(f"─────────────────────────────────")
    print(f"  Distance    : {DISTANCE_METERS * 100:.1f} cm")
    print(f"  Time taken  : {elapsed_ms} ms")
    print(f"  Speed       : {speed_kmh} km/h")
    print(f"  Status      : {status}")
    print(f"─────────────────────────────────")

    # Upload to ThingSpeak
    upload_to_thingspeak(speed_kmh, elapsed_ms, status)


# ─────────────────────────────────────────────
#  ATTACH INTERRUPTS
# ─────────────────────────────────────────────
def attach_interrupts():
    """
    FALLING edge = beam goes from HIGH to LOW = object broke the beam
    bouncetime in ms helps filter electrical noise
    """
    GPIO.add_event_detect(
        SENSOR_1_PIN,
        GPIO.FALLING,
        callback=sensor1_triggered,
        bouncetime=int(DEBOUNCE_TIME * 1000)
    )

    GPIO.add_event_detect(
        SENSOR_2_PIN,
        GPIO.FALLING,
        callback=sensor2_triggered,
        bouncetime=int(DEBOUNCE_TIME * 1000)
    )

    print("[Interrupts] Edge detection attached to both sensors")


# ─────────────────────────────────────────────
#  SENSOR SELF TEST
# ─────────────────────────────────────────────
def self_test():
    print("\n[Self Test] Checking sensor states...")
    s1 = GPIO.input(SENSOR_1_PIN)
    s2 = GPIO.input(SENSOR_2_PIN)

    s1_status = "OK (beam intact)" if s1 == GPIO.HIGH else "⚠ BEAM BROKEN or disconnected"
    s2_status = "OK (beam intact)" if s2 == GPIO.HIGH else "⚠ BEAM BROKEN or disconnected"

    print(f"  Sensor 1 → {s1_status}")
    print(f"  Sensor 2 → {s2_status}")

    if s1 == GPIO.HIGH and s2 == GPIO.HIGH:
        print("[Self Test] ✓ Both sensors ready!\n")
        return True
    else:
        print("[Self Test] ✗ Check wiring before proceeding!\n")
        return False


# ─────────────────────────────────────────────
#  PRINT BANNER
# ─────────────────────────────────────────────
def print_banner():
    print("=" * 50)
    print("   IoT Speed Monitoring System")
    print("   Raspberry Pi + IR Break-Beam Sensors")
    print("   ThingSpeak Dashboard")
    print("=" * 50)
    print(f"  Sensor distance : {DISTANCE_METERS * 100:.1f} cm")
    print(f"  Fast threshold  : {SPEED_FAST} km/h")
    print(f"  Slow threshold  : {SPEED_SLOW} km/h")
    print(f"  Upload cooldown : {UPLOAD_COOLDOWN}s")
    print("=" * 50)
    print("  Waiting for objects...\n")


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────
def main():
    print_banner()

    try:
        setup_gpio()
        self_test()
        attach_interrupts()

        # Keep the main thread alive
        # All work happens in interrupt callbacks
        while True:
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n\n[System] Stopped by user (Ctrl+C)")

    finally:
        GPIO.cleanup()
        print("[GPIO] Pins cleaned up. Goodbye!")


if __name__ == "__main__":
    main()
