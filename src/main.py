import sys
import paho.mqtt.client as mqtt
import components.car.run as car
import components.charger.run as charger
import components.app.run as app
import components.server.run as server
import components.server.mqtt as mqttServer

#server.run()
app1 = app.App()
car.BatteryComponent()
charger.ChargerComponent()
