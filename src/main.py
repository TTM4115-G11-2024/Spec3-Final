import sys
import paho.mqtt.client as mqtt
import components.car.car as car
import components.charger.charger as charger
import components.app.run as app
import components.server.run as server
import components.server.mqtt as mqttServer

MQTT_BROKER = "test.mosquitto.org"
MQTT_PORT = 1883

CAR_TOPIC = "ttm4115/g11/cars"
CHARGER_TOPIC = "ttm4115/g11/chargers"

app1 = app.App()
server_mqtt = mqttServer.MQTTClient()
charger1 = app1.selected_station 
car1 = app1.car_id

mqtt_client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION1)
mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
mqtt_client.subscribe(f"{CAR_TOPIC}/{app1.car_id}")
server_mqtt.send_start_charging_to_charger(charger1, car1, app1.chosen_percentage)
server_mqtt.send_start_charging_to_car(charger1, car1)

'''mqtt_client.publish(f"{CAR_TOPIC}/{app1.car_id}", {
  "charger_id": app1.start_charging,
  "car_id": app1.car_id,
  "battery_target": app1.chosen_percentage,
})'''
