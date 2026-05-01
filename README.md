# iot-vehicle-speed-monitor
### Major Project | IR Break-Beam Sensors + Raspberry Pi + ThingSpeak 2025
An IoT-based speed tracking system that uses a Raspberry Pi and dual IR break-beam sensors to calculate object velocity and log real-time data to ThingSpeak.

## Overview
A real-time speed monitoring system that measures the velocity of a moving object
(such as a toy car on a track) using two IR break-beam sensors placed a known
distance apart. The Raspberry Pi timestamps the moment each sensor beam is broken,
calculates speed in km/h, classifies it as FAST / NORMAL / SLOW, and uploads the
results to the ThingSpeak cloud platform. This mimics speed-monitoring systems used
on roads, conveyor belts, and production lines.
## How It Works
1. Object approaches the track — both IR beams are intact (sensors output HIGH)
2. Object breaks **IR Sensor 1** (START gate) — GPIO17 goes LOW → interrupt fires
3. Raspberry Pi records the exact start timestamp
4. Object travels the measured distance and breaks **IR Sensor 2** (END gate)
5. Raspberry Pi records the end timestamp and computes elapsed time
6. Speed (km/h) is calculated: `Speed = (Distance / Time) × 3.6`
7. Speed is classified: FAST (≥ 10 km/h), SLOW (≤ 2 km/h), or NORMAL
8. Results are printed to the terminal and uploaded to ThingSpeak via WiFi
## Hardware Required
- Raspberry Pi (any model with GPIO — Pi 3B / 4 recommended)
- 2× IR Break-Beam Sensor modules
- Breadboard and jumper wires
- USB power supply for Raspberry Pi
- Ruler / measuring tape (to set the sensor distance accurately)
- Toy car / track or any moving object for testing
## Wiring
### IR Sensor 1 — START Gate
| IR Sensor Pin | Raspberry Pi Pin       |
|---------------|------------------------|
| VCC           | Pin 2  (5V)            |
| GND           | Pin 6  (GND)           |
| OUT           | GPIO17 — Pin 11        |
### IR Sensor 2 — END Gate
| IR Sensor Pin | Raspberry Pi Pin       |
|---------------|------------------------|
| VCC           | Pin 4  (5V)            |
| GND           | Pin 9  (GND)           |
| OUT           | GPIO27 — Pin 13        |
> **Note:** IR break-beam sensors output **HIGH** when beam is intact and go
> **LOW** when the beam is broken. Internal pull-up resistors are enabled in
> software (`GPIO.PUD_UP`) — no external resistors required.
> **Important:** Measure the distance between both sensors accurately with a
> ruler and update `DISTANCE_METERS` in the code accordingly.
## Software Required
- Raspberry Pi OS (Raspbian)
- Python 3
- Libraries:
  - `RPi.GPIO` (pre-installed on Raspberry Pi OS)
  - `requests` — install via: `pip3 install requests`
  - `datetime`, `time` (Python built-ins)
## Cloud Platform
- ThingSpeak IoT — https://thingspeak.com
- Field 1 → Speed (km/h)
- Field 2 → Time taken (ms)
- Field 3 → Status (FAST / NORMAL / SLOW)
## Setup Instructions
1. Connect IR sensors to Raspberry Pi as per the wiring table above
2. Install the `requests` library:
   ```bash
   pip3 install requests
   ```
3. Create a free ThingSpeak account at https://thingspeak.com
4. Create a new channel with 3 fields:
   - Field 1: Speed (km/h)
   - Field 2: Time (ms)
   - Field 3: Status
5. Copy your **Write API Key** from the ThingSpeak channel
6. Open `speed_monitor.py` and update the following:
   ```python
   DISTANCE_METERS      = 0.20          # Set exact sensor spacing in meters
   THINGSPEAK_WRITE_KEY = "YOUR_KEY"    # Replace with your Write API Key
   SPEED_FAST           = 10.0          # Adjust threshold if needed
   SPEED_SLOW           = 2.0           # Adjust threshold if needed
   ```
7. Run the script:
   ```bash
   python3 speed_monitor.py
   ```
8. Pass an object through both sensors and observe the output
## Expected Output
**Terminal (SSH / Console):**
```
==================================================
   IoT Speed Monitoring System
   Raspberry Pi + IR Break-Beam Sensors
   ThingSpeak Dashboard
==================================================
  Sensor distance : 20.0 cm
  Fast threshold  : 10.0 km/h
  Slow threshold  : 2.0 km/h
  Upload cooldown : 15s
==================================================
  Waiting for objects...
[GPIO] Pins configured successfully
[GPIO] Sensor 1 → GPIO17
[GPIO] Sensor 2 → GPIO27
[Self Test] ✓ Both sensors ready!
[Sensor 1] ⚡ Object detected at 14:32:05.412
[Sensor 1] Timing started — waiting for Sensor 2...
[Sensor 2] ⚡ Object detected at 14:32:05.672
─────────────────────────────────
  Distance    : 20.0 cm
  Time taken  : 260.0 ms
  Speed       : 2.77 km/h
  Status      : NORMAL
─────────────────────────────────
[ThingSpeak] ✓ Data uploaded! Entry ID: 18342
```
## Key Parameters
| Parameter          | Value / Default        |
|--------------------|------------------------|
| Sensor 1 GPIO      | GPIO17 (Pin 11)        |
| Sensor 2 GPIO      | GPIO27 (Pin 13)        |
| Sensor spacing     | 0.20 m (20 cm)         |
| Speed formula      | (Distance ÷ Time) × 3.6 |
| FAST threshold     | ≥ 10.0 km/h            |
| SLOW threshold     | ≤ 2.0 km/h             |
| Debounce time      | 50 ms                  |
| ThingSpeak cooldown| 15 seconds             |
| Trigger edge       | FALLING (beam broken)  |
| GPIO mode          | BCM                    |
## Block Diagram
![Block Diagram](block_diagram.png)
## Project Structure
```
├── speed_monitor.py              # Main Python script — all logic
├── speed_monitor_block_diagram.html  # System block diagram (open in browser)
└── README.md
```
## Stopping the Script
Press `Ctrl + C` to stop. GPIO pins are automatically cleaned up on exit.
## License
This project is open-source and free to use for educational purposes.
