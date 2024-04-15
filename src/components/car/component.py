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
MQTT_TOPIC_INPUT = "charger_percent"
MQTT_TOPIC_OUTPUT = "charger_percent"


class CarBattery:
    def __init__(self, perc, act_perc):
        self.connected = False
        self.wanted_perc = perc
        self.actual_perc = act_perc

    def charger_plugged(self):
        self.charger_connected = True
        print(self.stm.driver.print_status())
        print("Car connected")

    def charger_unplugged(self):
        self.charger_connected = False
        print(self.stm.driver.print_status())
        print("Car disconnected")

    def send_update(self, update, charger):
        self.charger.send(
            "percentage"
        )  # car sends to charger how much battery it has left
        print(self.stm.driver.print_status())

    def charged_compound_transition(self):
        percentage = self.wanted_perc
        if self.actual_perc == percentage:
            print("Charging completed!")
            print(self.stm.driver.print_status())
            return "idle"
        else:
            self.actual_perc += 1
            print(self.stm.driver.print_status())
            return "charging"


battery = CarBattery()

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
idle_to_final = {
    "trigger": "charger_unplugged",
    "source": "idle",
    "target": "final",
}

# the states:
charging = {
    "name": "charging",
    "entry": "send_update(update, charger); start_timer('t', 500)",
}
# idle = { "name": "idle",
#        "entry": ""
# }


# create the State Machine
car_battery_machine = Machine(
    transitions=[initial_to_charging, charging_to_choose, idle_to_final],
    obj=battery,
    name="car_battery",
)
battery.stm = car_battery_machine

# create a driver
driver = Driver()
# add our state machine to the driver
driver.add_machine(car_battery_machine)
# start driver
driver.start(max_transitions=30)


class MQTT_Client:
    def __init__(self):
        self.battery_percentage = random.randrange(10, 30)
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        print("on_connect(): {}".format(mqtt.connack_string(rc)))

    def on_message(self, client, userdata, msg):
        print("on_message(): topic: {}".format(msg.topic))
        self.stm_driver.send("message", "tick_tock")

    def start(self, broker, port):

        print("Connecting to {}:{}".format(broker, port))
        self.client.connect(broker, port)

        self.client.subscribe("ttm4115")

        try:
            # line below should not have the () after the function!
            thread = Thread(target=self.client.loop_forever)
            thread.start()
        except KeyboardInterrupt:
            print("Interrupted")
            self.client.disconnect()
