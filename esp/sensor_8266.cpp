#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <PubSubClient.h>


const char* ssid = ""; 
const char* password = "";
const char* mqtt_server = ""; 


const int trigPin = 5;   
const int echoPin = 4;   
const int redLed  = 14;  
const int greenLed = 12; 

WiFiClient espClient;
PubSubClient client(espClient);


bool isCarParked = false; 
const int threshold = 20; 

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to WiFi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println(" Connected!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    String clientId = "ParkingSensor-" + String(random(0xffff), HEX);
    if (client.connect(clientId.c_str())) {
      Serial.println("Connected to Broker!");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 3 seconds");
      delay(3000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  pinMode(redLed, OUTPUT);
  pinMode(greenLed, OUTPUT);

  
  digitalWrite(redLed, LOW);
  digitalWrite(greenLed, HIGH); 
  
  setup_wifi();
  client.setServer(mqtt_server, 1883);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  
  digitalWrite(trigPin, LOW); delayMicroseconds(2);
  digitalWrite(trigPin, HIGH); delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  
  long duration = pulseIn(echoPin, HIGH);
  int distance = duration * 0.034 / 2;

  
  if (distance == 0 || distance > 400) return;

  Serial.print("Dist: "); Serial.println(distance); 

  
  
  
  if (distance > 4 && distance < threshold && isCarParked == false) {
    delay(500); 
    
    digitalWrite(trigPin, LOW); delayMicroseconds(2);
    digitalWrite(trigPin, HIGH); delayMicroseconds(10); digitalWrite(trigPin, LOW);
    int checkDist = pulseIn(echoPin, HIGH) * 0.034 / 2;

    if (checkDist > 4 && checkDist < threshold) {
      Serial.println("--> Status: OCCUPIED");
      digitalWrite(redLed, HIGH);
      digitalWrite(greenLed, LOW);
      client.publish("parking/slot1", "OCCUPIED");
      isCarParked = true;
    }
  }
  
  
  else if (distance > threshold && isCarParked == true) {
    delay(500); 
    
    digitalWrite(trigPin, LOW); delayMicroseconds(2);
    digitalWrite(trigPin, HIGH); delayMicroseconds(10); digitalWrite(trigPin, LOW);
    int checkDist = pulseIn(echoPin, HIGH) * 0.034 / 2;

    if (checkDist > threshold) {
      Serial.println("--> Status: FREE");
      digitalWrite(redLed, LOW);
      digitalWrite(greenLed, HIGH);
      client.publish("parking/slot1", "FREE");
      isCarParked = false;
    }
  }
  
  delay(100);
}