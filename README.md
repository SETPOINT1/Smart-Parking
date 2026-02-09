# Smart Parking System (LPR & IoT)

[![Python](https://img.shields.io/badge/Language-Python_3.x-blue?logo=python&logoColor=white)](https://www.python.org/)
[![C++](https://img.shields.io/badge/Language-C++-00599C?logo=c%2B%2B&logoColor=white)](https://isocpp.org/)
[![Raspberry Pi](https://img.shields.io/badge/Hardware-Raspberry_Pi_4-C51A4A?logo=raspberry-pi&logoColor=white)](https://www.raspberrypi.com/)
[![ESP32](https://img.shields.io/badge/Hardware-ESP32-red?logo=espressif&logoColor=white)](https://docs.espressif.com/projects/arduino-esp32/en/latest/)
[![YOLOv8](https://img.shields.io/badge/AI-YOLOv8-purple)](https://docs.ultralytics.com/)
[![OpenCV](https://img.shields.io/badge/Vision-OpenCV-green?logo=opencv&logoColor=white)](https://opencv.org/)
[![n8n](https://img.shields.io/badge/Automation-n8n-ff6584?logo=n8n&logoColor=white)](https://n8n.io/)
[![Google Sheets](https://img.shields.io/badge/Database-Google_Sheets-34A853?logo=google-sheets&logoColor=white)](https://www.google.com/sheets/about/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A real-time **License Plate Recognition (LPR)** system for automated parking management combined with **IoT Slot Monitoring**. This project integrates **Edge AI (Raspberry Pi + YOLOv8)** for vehicle detection and **Low-Code Automation (n8n)** for data processing, OCR, and cloud storage.

The system supports dual-lane monitoring (Entry & Exit), automatic data validation, duplicate prevention, parking fee calculation, and real-time parking slot availability.

---

## Contents
1. [Project Details](#project-details)
2. [System Architecture](#system-architecture)
3. [Hardware Requirements](#hardware-requirements)
4. [Software & Frameworks](#software--frameworks)
5. [Installation & Setup](#installation--setup)
6. [Usage](#usage)
7. [Project Structure](#project-structure)
8. [License](#License)
9. [Demo & Presentation](#demo--presentation)

---

## Project Details
**Course:** CN360 Digital and Microcontroller System Development  
**Institution:** Department of Computer Engineering, Faculty of Engineering, Thammasat University.

### Development Team
1. **Chonchanan Jitrawang**
2. **Kittidet Wichaidit**
3. **Thanabodee Suddaen**

---

## System Architecture

The system is divided into three main parts: **Edge Processing** (Raspberry Pi), **IoT Sensors** (ESP32), and **Cloud Backend** (n8n).

![Smart parking CN360](https://github.com/user-attachments/assets/239f3e2b-6cde-4b2c-aada-0e04ad632950)


### Key Features

* **Multi-Camera Support:** Handles both Entry and Exit lanes simultaneously using multi-threading.
* **Object Detection:** Uses **YOLOv8** to detect license plates in real-time.
* **Real-time Slot Monitoring:** Uses Ultrasonic sensors to detect vehicle presence and update status via LED indicators and display slots availability on an I2C LCD screen at the entry gate.
* **Cloud OCR:** Integrates with OCR APIs (OCR.space) for text extraction.
* **Smart Validation:**
    * **Province Whitelist:** Validates Thai province names against a predefined database.
    * **Deduplication:** Prevents duplicate entries within a specific cooldown period.
* **Fee Calculation:** Automatically calculates parking duration and fees (e.g., Free for the first 4 hours).
* **Hardware Feedback:** Displays status and fees on an I2C LCD screen at the exit gate.

---

## Hardware Requirements

1. **Core Processing:** Raspberry Pi 4 Model B (Main Controller).
2. **IoT Microcontroller:** ESP32 / ESP8266 (Sensor control).
3. **Vision & Interface:** 
   * Smartphone Camera (running IP Webcam app).
   * LCD 16x2 Display (I2C).
4. **Sensors & Actuators:** 
   * Ultrasonic Sensors (HC-SR04).
   * LED Indicators (Red/Green).
   * Breadboard & Jumper wires.

---

## Software & Frameworks

1. **Computer Vision:** OpenCV, YOLOv8 (for object detection).
2. **Automation:** n8n (Workflow Automation).
3. **Database:** Google Sheets (Cloud storage & OCR logging).
4. **Communication:** Webhooks (HTTP), MQTT protocol (for sensors).

---

## Installation & Setup

### 1. Raspberry Pi Setup (Client Side)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/SETPOINT1/Smart-Parking.git
   cd Smart-Parking/RPi
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Download the YOLO Model:**
   Ensure `LicensePlate.pt` is located in the `RPi/` directory.

4. **Configure Scripts:**
   * Edit `send_plates.py`: Update Camera URLs (IP Webcam) and n8n Webhook URL.
   * Edit `slots.py`: Configure GPIO pins or API endpoints for the ESP32 connection.

### 2. ESP32/ESP8266 Setup (Sensors)

1. Navigate to the `esp/` folder.
2. Open `sensor_32.cpp` (for ESP32) or `sensor_8266.cpp` (for ESP8266).
3. Update **Wi-Fi Credentials** (SSID/Password) and **Server IP** (Raspberry Pi IP).
4. Flash the code to your microcontroller using Arduino IDE.

### 3. Google Sheets Setup (Database)

Create a new Google Sheet with the following headers in Row 1:
| A | B | C | D | E | F | G | H |
|---|---|---|---|---|---|---|---|
| **Timestamp_In** | **Plate_Number** | **Province** | **Status** | **Timestamp_Out** | **Duration** | **Fee** | **Raw_Text** |

### 4. n8n Workflow Setup (Server Side)

1. **Import Workflow:** Import the `n8n/Workflow.json` file into your n8n instance.
2. **Credentials:** Configure your Google Drive/Sheets and OCR API credentials within n8n nodes.

---

## Usage

1. **Start the n8n workflow** (set to **Active**).
2. **Run the Parking Slot Monitor:**
   ```bash
   cd Smart-Parking/RPi
   python slots.py
   ```
3. **Run the LPR System:**
   Open a new terminal and run:
   ```bash
   cd Smart-Parking/RPi
   python send_plates.py
   ```

**System Behavior:**
* **Entry Gate:** Camera detects plate -> Sends to n8n -> Logs to Sheets.
* **Parking Slot:** Ultrasonic sensor detects car -> LED turns Red -> Updates system.
* **Exit Gate:** Camera detects plate -> n8n calculates fee -> LCD shows "Fee: XX Baht".

---

## Project Structure

```text
Smart-Parking/
├── RPi/                        # Raspberry Pi Source Code
│   ├── I2C_LCD_driver_Bus3.py  # LCD I2C Driver Library
│   ├── LicensePlate.pt         # YOLOv8 Trained Model
|   ├── requirements.txt
│   ├── send_plates.py          # Main Logic: Detection & HTTP Request
│   └── slots.py                # Parking Slot Management Logic
├── esp/                        # Microcontroller Code
│   ├── sensor_32.cpp           # Code for ESP32
│   └── sensor_8266.cpp         # Code for ESP8266
├── n8n/                        # Backend Automation
│   ├── Workflow.json           # n8n Workflow Export File
└── README.md                   # Main Project Documentation
```

---

## License

Distributed under the MIT License. See [`LICENSE`](LICENSE) for more information.

*This project was developed for educational purposes as part of the **CN360 Digital and Microcontroller System Development** course, Thammasat University.*
---
## Demo & Presentation
Click the button below to watch our presentation and system demonstration.

[![Google Drive](https://img.shields.io/badge/Google_Drive-Watch_Videos-FBBC04?style=for-the-badge&logo=google-drive&logoColor=white)](https://drive.google.com/drive/folders/1AJlY7i6rjKTz-X9y6VWky1FP09h6Fgns?usp=drive_link)
