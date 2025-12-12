import time
import paho.mqtt.client as mqtt
from RPLCD.i2c import CharLCD


MQTT_BROKER = "localhost"
MQTT_TOPIC = "parking/+"  


TOTAL_SLOTS = 2
current_status = {} 


try:
    lcd = CharLCD(i2c_expander='PCF8574', address=0x27, port=1,
                  cols=16, rows=2, dotsize=8)
    lcd.clear()
except:
    lcd = None
    print("LCD Not Found")

def update_lcd():
    
    occupied_count = list(current_status.values()).count("OCCUPIED")
    available = TOTAL_SLOTS - occupied_count

    # ป้องกันเลขติดลบ
    if available < 0: available = 0

    print(f"Status Update: Available {available}/{TOTAL_SLOTS}")

    if lcd:
        lcd.clear()
        lcd.cursor_pos = (0, 0)
        lcd.write_string("SMART PARKING")
        lcd.cursor_pos = (1, 0)
        lcd.write_string(f"Empty: {available}/{TOTAL_SLOTS} Slots")

# === MQTT EVENTS ===
def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker")
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    topic = msg.topic              # เช่น parking/slot1
    payload = msg.payload.decode() # เช่น OCCUPIED หรือ FREE
    slot_id = topic.split("/")[-1] # ดึงชื่อ slot1 ออกมา

    print(f"Recv [{slot_id}]: {payload}")

    # อัปเดตสถานะลงตัวแปร
    current_status[slot_id] = payload

    # คำนวณที่ว่างใหม่และขึ้นจอ
    update_lcd()

# === MAIN LOOP ===
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

try:
    client.connect(MQTT_BROKER, 1883, 60)
    update_lcd() 
    print("📡 Waiting for ESP8266...")
    client.loop_forever() 
except KeyboardInterrupt:
    print("Stopping...")
