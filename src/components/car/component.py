'''import json
import logging
import random
import time
from threading import Thread

import ipywidgets as widgets
import paho.mqtt.client as mqtt
import stmpy
from IPython.display import display
from stmpy import Driver, Machine

current_battery_percentage = random.randrange(10, 30)


mqttBroker = "mqtt.eclipseprojects.io"
client = mqtt.Client("Charger")
client.connect(mqttBroker)

client.loop_forever()
client.subscribe("komsysgroup11spec3")


while True:
    client.publish(f"b{current_battery_percentage}")
    time.sleep(5)


class CarBattery:
    def __init__(self, perc):
        self.battery_percentage = random.randrange(10, 30)  # actual battery of the car
        self.charger_connected = False
        self.wanted_perc = perc

    def charger_plugged(self):
        self.charger_connected = True
        print(self.stm.driver.print_status())
        print("Car connected")

    def charger_unplugged(self):
        self.charger_connected = False
        print(self.stm.driver.print_status())
        print("Car disconnected")

    def send_update(self):
        print("send update")
        self.mqtt_client.publish("charger_percent", self.battery_percentage)  #car sends to charger how much battery it has left
        print(self.stm.driver.print_status())

    def charged_compound_transition(self):
        percentage = self.wanted_perc
        if self.battery_percentage == percentage:
            print("Charging completed!")
            print(self.stm.driver.print_status())
            return "idle"
        elif self.battery_percentage > percentage:
            print("Charging completed!")
            print(self.stm.driver.print_status())
            return "idle"
        else:
            self.battery_percentage += 1
            print(self.battery_percentage)
            print(self.stm.driver.print_status())
            return "charging"


battery = CarBattery(90)

# initial transition
initial_to_charging = {
    "source": "initial",
    "target": "charging",
    "effect": "charger_plugged",
}

# compound transition
charging_to_choose = {
    "trigger": "t",
    "source": "charging",
    "function": battery.charged_compound_transition,
}

# the other regular transition
idle_to_final = {"trigger": "charger_unplugged", "source": "idle", "target": "final"}

#the states:
charging = { 'name': 'charging',
            'entry': 'start_timer("t", 500)'
}

idle = {"name": "idle"}


class MQTT_Client_1:
    def __init__(self):
        self.battery_percentage = random.randrange(10, 30)
        self.client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION1)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_message(self, msg):
        if msg == "connected":
            self.charger_plugged
        else:
            self.charger_unplugged

    def send_battery_level(self, msg):
        self.client.publish(self.battery_percentage, msg.payload)
        self.battery_percentage += 1

    def charger_plugged(self):
        self.charger_connected = True
        print(self.stm.driver.print_status())
        print("Car connected")

    def charger_unplugged(self):
        self.charger_connected = False
        print(self.stm.driver.print_status())
        print("Car disconnected")

    def start(self, broker, port):
        # self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        print("Connecting to {}:{}".format(MQTT_BROKER, MQTT_PORT))
        self.client.connect(MQTT_BROKER, MQTT_PORT)
        
        self.client.subscribe("charger_percent")


# create the State Machine
car_battery_machine = Machine(
    transitions=[initial_to_charging, charging_to_choose, idle_to_final],
    obj=battery,
    name="car_battery",
    states=[charging, idle],
)
battery.stm = car_battery_machine

# create a driver
driver = Driver()
# add our state machine to the driver
driver.add_machine(car_battery_machine)

myclient = MQTT_Client_1()
battery.mqtt_client = myclient.client
myclient.stm_driver = driver

# start driver
driver.start(max_transitions=100)


'''
from stmpy import Machine, Driver

import ipywidgets as widgets
from IPython.display import display
import paho.mqtt.client as mqtt
import stmpy
import logging
from threading import Thread
import json
import random

# TODO: choose proper MQTT broker address
MQTT_BROKER = "test.mosquitto.org"
MQTT_PORT = 1883

# TODO: choose proper topics for communication
MQTT_TOPIC = ["ttm4115/g11/cars/", "ttm4115/g11/chargers/"]


class CarBattery:
    def __init__(self, perc, carID):
        self.battery_percentage = random.randrange(10, 30)  #actual battery of the car
        self.charger_connected = False
        self.wanted_perc = perc
        self.car_ID = carID
        self.chargerID = 10 #TODO: how does the car know the chargerID to which it is connected

    def charger_plugged(self):
        self.charger_connected = True
        print(self.stm.driver.print_status())
        self.mqtt_client.publish(MQTT_TOPIC[1] + str(self.chargerID), "car" + str(self.car_ID) + "connected")  
        #car sends to charger confirmation that it has been connected (the message is NOT received in MQTT)
        print("send " + MQTT_TOPIC[1] + str(self.chargerID))
        #car sends ID to charger so that it can check wheter it is allow to charge or not
        print("Car connected")

    def charger_unplugged(self):
        self.charger_connected = False
        print(self.stm.driver.print_status())
        print("Car disconnected")

    def send_update(self):
        print("send update")
        self.mqtt_client.publish(MQTT_TOPIC[0] + str(self.car_ID), "b" + str(self.battery_percentage))  
        #car sends to charger how much battery it has left, it has the format bXX
        print(self.battery_percentage)
        print(self.stm.driver.print_status())

    def charged_compound_transition(self):
        percentage = self.wanted_perc
        if self.battery_percentage == percentage: 
            print("Charging completed!")
            print(self.stm.driver.print_status())
            return 'idle'
        elif self.battery_percentage > percentage:
            print("Charging completed!")
            print(self.stm.driver.print_status())
            return 'idle'
        else:
            self.battery_percentage += 1
            print(self.battery_percentage)
            print(self.stm.driver.print_status())
            return 'charging'

battery = CarBattery(90, "AB12345")

#initial transition
initial_to_charging = {
    'source': 'initial',
    'target': 'charging',
    'effect': 'charger_plugged'
}

#compound transition
charging_to_choose = {
    'trigger': 't',
    'source': 'charging',
    'function': battery.charged_compound_transition
}

#the other regular transition
idle_to_final = {
    'trigger': 'charger_unplugged',
    'source': 'idle',
    'target': 'final'
}

#the states:
charging = { 'name': 'charging',
            'entry': 'send_update; start_timer("t", 500)'
}

idle = { 'name': 'idle'
}   


class MQTT_Client_1:
    def __init__(self):
        self.battery_percentage = random.randrange(10, 30)
        self.client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION1)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        print("on_connect(): {}".format(mqtt.connack_string(rc)))

    def on_message(self, msg):
        if msg == "connected":
            self.charger_plugged
        else:
            self.charger_unplugged

    def send_battery_level(self, msg):
        self.client.publish(self.battery_percentage, msg.payload)
        self.battery_percentage += 1

    def charger_plugged(self):
        self.charger_connected = True
        print(self.stm.driver.print_status())
        print("Car connected")

    def charger_unplugged(self):
        self.charger_connected = False
        print(self.stm.driver.print_status())
        print("Car disconnected")

    def start(self, broker, port):
        #self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        print("Connecting to {}:{}".format(MQTT_BROKER, MQTT_PORT))
        self.client.connect(MQTT_BROKER, MQTT_PORT)
        #for topic in MQTT_TOPIC:
            #self.client.subscribe(topic)
        self.client.subscribe(MQTT_TOPIC[0])
        self.client.subscribe(MQTT_TOPIC[1])

       
#create the State Machine
car_battery_machine = Machine(transitions=[initial_to_charging,charging_to_choose,idle_to_final], obj=battery, name='car_battery', states=[charging, idle])
battery.stm = car_battery_machine

#create a driver
driver = Driver()
#add our state machine to the driver
driver.add_machine(car_battery_machine)

myclient = MQTT_Client_1()
battery.mqtt_client = myclient.client
myclient.stm_driver = driver

#start driver
driver.start(max_transitions=100)
myclient.start(MQTT_BROKER, MQTT_PORT)