from stmpy import Machine, Driver

import paho.mqtt.client as mqtt
import stmpy
import json

# TODO: choose proper MQTT broker address
MQTT_BROKER = "test.mosquitto.org"
MQTT_PORT = 1883

# TODO: choose proper topics for communication
CAR_TOPIC = "ttm4115/g11/cars"
CHARGER_TOPIC = "ttm4115/g11/chargers"


class BatteryLogic:
    def __init__(self, car_id, mqtt_client):
        self.car_id = car_id
        self.mqtt_client: mqtt.Client = mqtt_client
        self.percentage = 10
        self.charger_id = None

        # Transitions
        transitions = [
            {"source": "initial", "target": "idle"},
            {"source": "idle", "target": "charging", "trigger": "start_charging", "effect": "effect_charging"},
            {"source": "charging", "target": "charging", "trigger": "update_timer", "effect": "effect_charging_update"},
            {"source": "charging", "target": "idle", "trigger": "finish_charging", "effect": "effect_finish_charging"}
        ]

        # States
        states = [
            {"name": "charging", "entry": "start_timer('update_timer', 500)"}
        ]

        # State machine
        self.stm = stmpy.Machine(
            name=car_id, 
            transitions=transitions, 
            states=states,
            obj=self
        )

    def init_stm(self):
        pass

    def effect_charging(self):
        print("Charging has started.")
        pass

    def effect_charging_update(self):
        self.percentage += 2
        print(f"Current battery percentage: {self.percentage}")
        topic = f"{CHARGER_TOPIC}/{self.charger_id}"
        payload = {"command": "battery_percentage", "percentage": self.percentage}
        payload = json.dumps(payload)

        self.mqtt_client.publish(topic, payload)

    def effect_finish_charging(self):
        print("Charging has finished.")
        self.driver.stop()
        pass


class BatteryComponent:
    def __init__(self, car_id):
        # mqtt definitions
        self.mqtt_client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION1)
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
        self.mqtt_client.subscribe(f"{CAR_TOPIC}/{car_id}")
        self.mqtt_client.loop_start()

        # stm definitions
        self.battery = BatteryLogic(car_id, self.mqtt_client)

        # driver
        self.stm_driver = stmpy.Driver()
        self.stm_driver.start(keep_active=True)
        self.stm_driver.add_machine(self.battery.stm)

        # other variables
        self.charger_id = None

    def on_message(self, client, userdata, msg):
        msg = json.loads(msg.payload)  # now a dict

        command = msg.get("command")

        # TODO determine what to do
        if command == "start_charging":
            charger_id = msg.get("charger_id")
            self.battery.charger_id = charger_id

            self.stm_driver.send("start_charging", self.battery.car_id)
        elif command == "stop_charging":
            self.stm_driver.send("finish_charging", self.battery.car_id)

    def on_connect(self, client, userdata, flags, rc):
        print("MQTT Connected")


# Initialize component
t = BatteryComponent("A100")
