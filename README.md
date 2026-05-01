# iot-vehicle-speed-monitor
### Major Project | IR Break-Beam Sensors + Raspberry Pi + ThingSpeak 2025
An IoT-based speed tracking system that uses a Raspberry Pi and dual IR break-beam sensors to calculate object velocity and log real-time data to ThingSpeak.

## Overview
A real-time speed monitoring system that measures the velocity of a moving object (such as a toy car on a track) using two IR break-beam sensors placed a known distance apart. The Raspberry Pi timestamps the moment each sensor beam is broken, calculates speed in km/h, classifies it as FAST / NORMAL / SLOW, and uploads the results to the ThingSpeak cloud platform. This mimics speed-monitoring systems used on roads, conveyor belts, and production lines.

## Block Diagram

<p align="center">
  <img width="1449" height="774" alt="System Block Diagram" src="https://github.com/user-attachments/assets/69e1594c-98d0-435a-acda-9ddf6cae4ea6" />
  <br>
  <em>Figure 1: Block diagram illustrating the system architecture and data flow.</em>
</p>

## System setup snapshot

<p align="center">
  <img width="100%" alt="IoT Vehicle Speed Monitor Hardware Setup" src="https://github.com/user-attachments/assets/f28411d8-fa91-4e9f-9c2e-382f26e7a4ea" />
  <br>
  <em>Figure 2: Physical hardware implementation of the IoT Vehicle Speed Monitor showing the Raspberry Pi and IR sensor alignment on the test track.</em>
</p>


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
- Thonny IDE
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

<p align="center">
  <img width="784" height="336" alt="ThingSpeak Credentials Location" src="https://github.com/user-attachments/assets/90ddd28a-8a26-428a-a25e-998c389549e9" />
  <br>
  <em>Figure 3: Locating ThingSpeak Credentials for Firmware.</em>
</p>

6. Open `speed_monitor.py` and update the following:
   ```python
   DISTANCE_METERS      = 0.86          # Set exact sensor spacing in meters
   THINGSPEAK_WRITE_KEY = "YOUR_KEY"    # Replace with your Write API Key
   SPEED_FAST           = 10.0          # Adjust threshold if needed
   SPEED_SLOW           = 2.0           # Adjust threshold if needed
   ```
7. Run the script:
   ```bash
   python3 speed_monitor.py
   ```
8. Pass an object through both sensors and observe the output

## Key Parameters
| Parameter          | Value / Default        |
|--------------------|------------------------|
| Sensor 1 GPIO      | GPIO17 (Pin 11)        |
| Sensor 2 GPIO      | GPIO27 (Pin 13)        |
| Sensor spacing     | 0.86 m (8.6 cm)         |
| Speed formula      | (Distance ÷ Time) × 3.6 |
| FAST threshold     | ≥ 10.0 km/h            |
| SLOW threshold     | ≤ 2.0 km/h             |
| Debounce time      | 50 ms                  |
| ThingSpeak cooldown| 15 seconds             |
| Trigger edge       | FALLING (beam broken)  |
| GPIO mode          | BCM                    |


## Expected Output

<!-- Figure 3: Serial Monitor Output -->
<p align="center">
  <img width="100%" alt="Serial Monitor Output Data" src="https://github.com/user-attachments/assets/2ea42aba-9873-4680-9a7a-3e5d8e2b694f" />
  <br>
  <em>Figure 4: Serial Monitor output displaying real-time sensor readings and successful cloud upload confirmations.</em>
</p>

<br><br> <!-- Space between figures -->

<!-- Figure 5: ThingSpeak Dashboard -->
<p align="center">
  <img width="100%" alt="ThingSpeak Cloud Dashboard" src="https://github.com/user-attachments/assets/0134d610-9529-4579-837a-68c4d8f4c15d" />
  <br>
  <em>Figure 5: ThingSpeak cloud dashboard visualizing the logged data points and trends over time.</em>
</p>



