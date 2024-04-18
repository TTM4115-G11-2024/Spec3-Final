import paho.mqtt.client as mqtt
import json
import time

MQTT_BROKER = "test.mosquitto.org"
MQTT_PORT = 1883

class MQTTClient:
    def __init__(self):
        self.client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION1)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        print("on_connect(): {}".format(mqtt.connack_string(rc)))

    def on_message(self, msg):
        return

    def send_start_charging_to_car(self, charger_id: int, car_id: str):
        payload = {
            "command": "start_charging",
            "charger_id": charger_id,
        }
        payload = json.dumps(payload)

        print(f"ttm4115/g11/cars/{car_id}")
        self.client.publish(f"ttm4115/g11/cars/{car_id}", payload)
        return
    
    def send_start_charging_to_charger(self, charger_id: int, car_id: str, battery_target: int):
        payload = {
            "command": "start_charging",
            "car_id": car_id,
            "battery_target": battery_target,
        }
        payload = json.dumps(payload)

        self.client.publish(f"ttm4115/g11/chargers/{charger_id}", payload)


    def start(self):
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        print("Connecting to {}:{}".format(MQTT_BROKER, MQTT_PORT))
        self.client.connect(MQTT_BROKER, MQTT_PORT)
    

    def stop(self):
        self.client.disconnect()

    
        