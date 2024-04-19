import logging
import json
import paho.mqtt.client as mqtt
from stmpy import Machine, Driver

# import sensehat as SH


# Configure the MQTT settings
MQTT_BROKER = "test.mosquitto.org"
MQTT_PORT = 1883
MQTT_TOPIC = "charger_percent"
# error_handler = SH.ErrorHandler()


# State machine logic for the Charger
class Charger:
    def __init__(self, charger_id, target_battery_percentage):
        self.charger_id = charger_id
        self.battery_percentage = 0
        self.target_battery_percentage = 100
        self.car_connected = False  # Indicates if car is connected
        self.is_activated = False  # Indicates if charger is activated
        self.is_reserved = False  # Indicates if charger is reserved
        self.reserved_by = None  # ID of user who reserved charger?
        self.target_battery_percentage = target_battery_percentage
        self.car_id = None  # Initi car_id

    def on_battery_update(self, battery_percentage):
        self.battery_percentage = int(battery_percentage)
        print(f"Received battery update: {self.battery_percentage}%")

        # Check if battery level reached
        if self.battery_percentage >= self.target_battery_percentage:
            self.stm.send("battery_level_reached")
            self.stop_charging()
            print("Charging stopped, battery level reached")

    def charger_nozzle_connected(self):
        self.charger_nozzle_connected = True
        print("Charger plugged to car.")

    def charger_nozzle_disconnected(self):
        self.charger_nozzle_disconnected = False
        self.stop_charging()
        print("Charger unplugged from car.")

    def start_charging(self, car_id, battery_target):
        self.car_id = car_id
        self.target_battery_percentage = int(battery_target)

        if self.car_connected and self.is_activated:
            self.is_activated = True
            print(f"Start charging the car {car_id} to {battery_target}")
            # Logic to start charging the car

    def stop_charging(self):
        if self.is_activated:
            self.is_activated = False
            car_id = self.car_id if self.car_id else "unknown"  # Fallback to 'unknown'
            print(f"Charging stopped for the car {car_id}")
            self.car_id = None  # Reset the car_id

    def error_occur(self):
        self.error = True
        # error_handler.start()

    def error_resolved(self):
        self.error = False
        # error_handler.stop()

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
        # TOPIC
        self.charger_topic = f"ttm4115/g11/chargers/{self.charger.charger_id}"
        print(self.charger_topic)

    # Initial connected message
    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected to MQTT Broker with charger_id {self.charger.charger_id}")

    # Battery percentage
    def on_message(self, client, userdata, msg):
        data = json.loads(msg.payload)

        """#Battery percentage 
        battery_percentage = data.get("battery_percentage")
        print(battery_percentage)
        """

        # Printing command just to see what is sent
        command = data.get("command")
        print(command)

        # Handles car id assuming car_id should match the car currently being charged
        car_id = data.get("car_id")
        if self.charger.car_id and car_id != self.charger.car_id:
            print(
                f"Ignoring update for car {car_id} as it does not match the current car {self.charger.car_id}, include car_id in the command"
            )
            return

        # Start charging and battery target
        if command == "start_charging":
            # Converting to int
            battery_target = int(data.get("battery_target"))
            self.charger.start_charging(car_id, battery_target)
            print(f"Charging started for car {car_id} with target {battery_target}%")

        # Handle stop_charging
        elif command == "stop_charging":
            self.charger.stop_charging()
            print(f"Charging stopped for car {self.charger.car_id}")

        # Handle battery percentage update
        elif command == "battery_percentage":
            # Converting to int
            battery_percentage = int(data.get("battery_percentage"))
            # Update the battery percentage of the charger
            self.charger.on_battery_update(battery_percentage)
            print(
                f"Battery update: {battery_percentage}% for car {self.charger.car_id}"
            )

    # Connection establishment
    def start(self):
        print(f"Connecting to {MQTT_BROKER}:{MQTT_PORT}")
        self.client.connect(MQTT_BROKER, MQTT_PORT)
        self.client.loop_start()
        self.client.subscribe(self.charger_topic)


# Logging
logging.basicConfig(level=logging.INFO)

# Charger instance and a corresponding MQTT client
charger1 = Charger(charger_id="001", target_battery_percentage=80)
mqtt_client_charger1 = MQTTClientCharger(charger1)

# Initial transition
initial_transition = {"trigger": "init", "source": "initial", "target": "idle"}

# Transitions and states
transitions = [
    initial_transition,  # Initial transition
    {"trigger": "init", "source": "initial", "target": "idle"},
    {
        "trigger": "charger_Nozzle_detected",
        "source": "idle",
        "target": "connected",
        # "effect": "charger_nozzle_detected",
    },
    {
        "trigger": "Charger_Nozzle_disconnected",
        "source": "connected",
        "target": "idle",
        "effect": "charger_nozzle_disconnected",
    },
    {
        "trigger": "Activated",
        "source": "connected",
        "target": "charging",
        "effect": "activate_charger",
        "condition": "user_has_reservation",
    },
    {
        "trigger": "battery_level_reached",
        "source": "charging",
        "target": "idle",
        "effect": "stop_charging",
    },
    {
        "trigger": "error",
        "source": "charging",
        "target": "error",
        "effect": "error_occur",
    },
    {
        "trigger": "error",
        "source": "connected",
        "target": "error",
        "effect": "error_occur",
    },
    {
        "trigger": "resolved",
        "source": "error",
        "target": "idle",
        "effect": "error_resolved",
    },
    {
        "trigger": "hw_failure",
        "source": "error",
        "target": None,
        "effect": "hardware_failure",
    },
]

# States
states = [
    {"name": "idle", "on_enter": "charger_nozzle_disconnected"},
    {"name": "connected", "on_enter": "charger_nozzle_detected"},
    {"name": "charging", "on_enter": "start_charging"},
    {"name": "error", "on_enter": "error_occur", "on_exit": "error_resolved"},
]

# State machine and add it to the charger object
stm = Machine(
    name="charger_machine", transitions=transitions, obj=charger1, states=states
)
charger1.stm = stm

# Driver and add the state machine to it
driver = Driver()
driver.add_machine(stm)

# Start  MQTT client and the state machine driver
mqtt_client_charger1.start()
driver.start()


"""{
  "command": "start_charging",
  "car_id": "car123",
  "battery_target": "80"
}


{
  "command": "battery_percentage",
  "battery_percentage": "70"
}

{
  "command": "battery_percentage",
  "car_id": "car123",
  "battery_percentage": "80"
}
"""
