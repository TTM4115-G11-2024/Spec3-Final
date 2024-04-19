import logging
import json
import paho.mqtt.client as mqtt
from stmpy import Machine, Driver


# Configure the MQTT settings
MQTT_BROKER = "test.mosquitto.org"
MQTT_PORT = 1883
MQTT_TOPIC = "charger_percent"

# State machine logic for the Charger
class Charger:
    def __init__(self, charger_id):
        self.charger_id = charger_id
        self.battery_percentage = 0
        self.car_connected = False

    def on_battery_update(self, battery_percentage):
        self.battery_percentage = battery_percentage
        print(f"Received battery update: {self.battery_percentage}%")
        # Logic to handle the battery update

    def is_reserved_and_correct_user(self):
        return True

    def charger_nozzle_detected(self):
        self.charger_nozzle_detected = True
        print("Charger plugged to car.")

    def charger_nozzle_disconnected(self):
        self.charger_nozzle_disconnected = False
        print("Charger unplugged from car.")

    def start_charging(self):
        print("Start charging.")
        # Logic to start charging the car

    def battery_level_reached(self):
        print("Stop charging, battery level reached.")
        # Logic to stop charging the car for the set timeslot?

    def error_occur(self):
        self.error = True
        print("An error occurred.")

    def error_resolved(self):
        self.error = False
        print("Error resolved.")

    def hardware_failure(self):
        print("Hardware failure detected. Shutting down.")
    # Do we need a def for send_to_specific_charger, or is this solved with charger id?


# The MQTT Client for the Charger
class MQTTClientCharger:
    def __init__(self, charger):
        self.client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION1)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.charger = charger
        #TOPIC
        self.charger_topic = f"ttm4115/g11/chargers/{self.charger.charger_id}"
        print(self.charger_topic)

    #Initial connected message
    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected to MQTT Broker with charger_id {self.charger.charger_id}")

    #Battery percentage 
    def on_message(self, client, userdata, msg):
        data = json.loads(msg.payload)
        battery_percentage = data.get("battery_percentage")
        command = data.get("command")   
        print(command)
        print(battery_percentage)

    #Connection establishment
    def start(self):
        print(f"Connecting to {MQTT_BROKER}:{MQTT_PORT}")
        self.client.connect(MQTT_BROKER, MQTT_PORT)
        self.client.loop_start()
        self.client.subscribe(self.charger_topic)


# Setup logging
logging.basicConfig(level=logging.INFO)

# Charger instance and a corresponding MQTT client
charger1 = Charger(charger_id='001')
mqtt_client_charger1 = MQTTClientCharger(charger1)

# Initial transition
initial_transition = {
    'trigger': 'init',
    'source': 'initial',
    'target': 'idle'
}

# Transitions and states
transitions = [
    initial_transition,  # Initial transition
    {'trigger': 'init', 'source': 'initial', 'target': 'idle'},
    {'trigger': 'Charger_Nozzle_detected', 'source': 'idle', 'target': 'connected', 'effect': 'charger_nozzle_detected'},
    {'trigger': 'Charger_Nozzle_disconnected', 'source': 'connected', 'target': 'idle', 'effect': 'charger_nozzle_disconnected'},
    {'trigger': 'Activated', 'source': 'connected', 'target': 'charging', 'effect': 'activate_charger', 'condition': 'user_has_reservation'},
    {'trigger': 'battery_level_reached', 'source': 'charging', 'target': 'idle', 'effect': 'stop_charging'},
    {'trigger': 'error', 'source': 'charging', 'target': 'error', 'effect': 'error_occur'},
    {'trigger': 'error', 'source': 'connected', 'target': 'error', 'effect': 'error_occur'},
    {'trigger': 'resolved', 'source': 'error', 'target': 'idle', 'effect': 'error_resolved'},
    {'trigger': 'hw_failure', 'source': 'error', 'target': None, 'effect': 'hardware_failure'},
]

# States
states = [
    {'name': 'idle', 'on_enter': 'charger_nozzle_disconnected'},
    {'name': 'connected', 'on_enter': 'charger_nozzle_detected'},
    {'name': 'charging', 'on_enter': 'start_charging'},
    {'name': 'error', 'on_enter': 'error_occur', 'on_exit': 'error_resolved'},
]

# State machine and add it to the charger object
stm = Machine(name="charger_machine", transitions=transitions, obj=charger1, states=states)
charger1.stm = stm

# Driver and add the state machine to it
driver = Driver()
driver.add_machine(stm)

# Start  MQTT client and the state machine driver
mqtt_client_charger1.start()
driver.start()
