import cv2
import time
import requests
import threading
from ultralytics import YOLO


display = None
try:
    import I2C_LCD_driver_Bus3
    display = I2C_LCD_driver_Bus3.lcd()
    display.lcd_clear()
    display.lcd_display_string("Exit Gate Ready", 1)
    print("LCD Loaded")
except Exception as e:
    print(f"LCD Error: {e}")


CAM_ENTRY_URL = ""  
CAM_EXIT_URL  = ""   


WEBHOOK_ENTRY_URL = "" 
WEBHOOK_EXIT_URL  = ""  

PLATE_MODEL_PATH = "/home/cn360/Desktop/LicensePlate-EdgeAI/LicensePlate.pt"
CONFIDENCE_THRESHOLD = 0.6
SEND_COOLDOWN = 5.0


class CameraStream:
    def __init__(self, src, name="Camera"):
        self.stream = cv2.VideoCapture(src)
        self.name = name
        (self.grabbed, self.frame) = self.stream.read()
        self.stopped = False

    def start(self):
        threading.Thread(target=self.update, args=()).start()
        return self

    def update(self):
        while True:
            if self.stopped:
                self.stream.release()
                return
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True


def safe_crop(img, x1, y1, x2, y2):
    h, w = img.shape[:2]
    return img[max(0, y1):min(h, y2), max(0, x1):min(w, x2)]

def upload_worker(image_array, target_url, gate_name):
    """ฟังก์ชันอัปโหลดรูปไปยัง URL ที่กำหนด และรับค่าตอบกลับเฉพาะขาออก"""
    
    if gate_name == "OUT" and display:
        display.lcd_clear()
        display.lcd_display_string("Processing...", 1)

    try:
       
        _, img_encoded = cv2.imencode('.jpg', image_array)
        files = {'file': ('plate.jpg', img_encoded.tobytes(), 'image/jpeg')}

       
        if gate_name == 'IN':
            response = requests.post(target_url, files=files, timeout=10)

        elif gate_name == 'OUT':
            response = requests.post(target_url, files=files, timeout=30)

        if response.status_code == 200:
            print(f"Upload {gate_name} Success")

            if gate_name == "OUT":
                try:
                    
                    data = response.json()

                    
                    msg_status = data.get("message", "Processing...")
                    msg_line1  = data.get("line1", "")
                    msg_line2  = data.get("line2", "")
                    should_open = data.get("open_gate", False)

                    print(f"[{gate_name}] Server Says: {msg_status}")
                    print(f"[{gate_name}] {msg_line1}")
                    print(f"[{gate_name}] {msg_line2}")
                   
                    if display:
                        display.lcd_clear()
                        display.lcd_display_string(msg_status, 1)
                        display.lcd_display_string(msg_line1, 2)
                    
                    if should_open:
                        print(f"[{gate_name}]  เปิดไม้กั้นอัตโนมัติ (จอดฟรี/จ่ายแล้ว)")
                        
                    else:
                        print(f"[{gate_name}]  ไม้กั้นปิด (รอชำระเงิน)")

                except ValueError:
                    
                    print(f"{gate_name}: Server response is not valid JSON")

        else:
            print(f"Upload {gate_name} Failed: {response.status_code}")

    except Exception as e:
        print(f"Upload Error ({gate_name}): {e}")


def main():
    print("Loading YOLO Model...")
    plate_model = YOLO(PLATE_MODEL_PATH)

    print("Connecting to Cameras...")
    
    cam_in = CameraStream(CAM_ENTRY_URL, "ENTRY").start()
    cam_out = CameraStream(CAM_EXIT_URL, "EXIT").start()
    time.sleep(1.0) 

    
    last_sent = {'IN': 0, 'OUT': 0}

    print("System Ready. Monitoring IN & OUT lanes...")
    print("Press 'q' to exit.")

    while True:
        
        cameras = [
            (cam_in, 'IN', WEBHOOK_ENTRY_URL),
            (cam_out, 'OUT', WEBHOOK_EXIT_URL)
        ]

        for cam, gate_name, webhook_url in cameras:
            frame = cam.read()
            if frame is None:
                continue

            results = plate_model(frame, conf=CONFIDENCE_THRESHOLD, verbose=False)[0]
            detected = False

            for box in results.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())

                
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

               
                current_time = time.time()
                if (current_time - last_sent[gate_name]) > SEND_COOLDOWN:

                    cropped_plate = safe_crop(frame, x1, y1, x2, y2)

                   
                    sender_thread = threading.Thread(
                        target=upload_worker,
                        args=(cropped_plate.copy(), webhook_url, gate_name)
                    )
                    sender_thread.start()

                    print(f"{gate_name} Gate Detected! Sending...")

                    last_sent[gate_name] = current_time
                    detected = True

                if detected:
                    break

            
            cv2.imshow(f"LPR Monitor - {gate_name}", frame)

        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cam_in.stop()
            cam_out.stop()
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()