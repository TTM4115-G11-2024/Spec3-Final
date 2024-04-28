import json
import paho.mqtt.client as mqtt
import stmpy
import audio
import requests

# import sensehat as SH


# Configure the MQTT settings
MQTT_BROKER = "test.mosquitto.org"
MQTT_PORT = 1883
CHARGER_TOPIC = "ttm4115/g11/chargers"
CAR_TOPIC = "ttm4115/g11/cars"
# error_handler = SH.ErrorHandler()


# State machine logic for the Charger
class ChargerLogic:
    def __init__(self, charger_id, component):
        self.component : ChargerComponent = component
        self.charger_id : int = charger_id

        transitions = [
            {"source": "initial", "target": "idle", "effect": "stm_init"},
            {"trigger": "nozzle_connected", "source": "idle", "target": "connected", "effect": "on_nozzle_connected"},
            {"trigger": "nozzle_disconnected", "source": "connected", "target": "idle", "effect": "on_nozzle_disconnected"},
            {"trigger": "start_charging", "source": "connected", "target": "charging", "effect": "on_start_charging"},
            {"trigger": "battery_charged", "source": "charging", "target": "connected","effect": "on_battery_charged"}, # should target be idle or connected?
            {"trigger": "battery_update", "source": "charging", "target": "charging", "effect": "on_battery_update"},
            # Error transitions
            {"trigger": "error", "source": "charging", "target": "error","effect": "on_error_occur"},
            {"trigger": "error", "source": "connected", "target": "error", "effect": "on_error_occur"},
            {"trigger": "resolved", "source": "error", "target": "idle", "effect": "on_error_resolved"},
            {"trigger": "hw_failure", "source": "error", "target": None, "effect": "on_hardware_failure"}
        ]

        self.stm = stmpy.Machine(name=f"charger-{self.charger_id}", transitions=transitions, obj=self)

        # other variables
        self.car_id = None
        self.battery_target = None
        self.current_car_battery = None

    def stm_init(self):
        self.stm.send("nozzle_connected") # for now nozzle is automatically connected

    
    def on_battery_update(self):

        # Check if battery level reached
        if self.current_car_battery >= self.battery_target:
            # send charging stopped to car
            topic = f"{CAR_TOPIC}/{self.car_id}"
            payload = {"command": "stop_charging"}
            payload = json.dumps(payload)
            self.component.mqtt_client.publish(topic, payload)

            self.stm.send("battery_charged")
            print(f"Received battery update: {self.current_car_battery}%. Charging stopped.")
        else:
            # display the charging percentage on sense hat
            print(f"Received battery update: {self.current_car_battery}%. Charging continues.")
            pass


    def on_nozzle_connected(self):
        print("Charger plugged to car.")


    def on_nozzle_disconnected(self):
        print("Charger unplugged from car.")


    def on_start_charging(self):
        print(f"Charging started for car {self.car_id} with target {self.battery_target}%")

        # send start charging to car
        topic = f"{CAR_TOPIC}/{self.car_id}"
        payload = {
            "command": "start_charging",
            "charger_id": self.charger_id,
        }
        payload = json.dumps(payload)
        self.component.mqtt_client.publish(topic, payload)

        audio.play_charging_started_sound()


    def on_battery_charged(self):
        print(f"Charging stopped for the car {self.car_id}")
        self.make_charger_available()
        self.car_id = None
        self.battery_target = None
        self.current_car_battery = None
        audio.play_charging_completed_sound()
        

    def on_error_occur(self):
        print("Error occurred")
        # error_handler.start()

    def on_error_resolved(self):
        print("Error resolved")


    def on_hardware_failure(self):
        print("Hardware failure detected. Shutting down.")

    
    def make_charger_available(self):
        url = f"http://localhost:8000/chargers/{self.charger_id}/deactivate"
        requests.post(url=url)



# The MQTT Client for the Charger
class ChargerComponent:
    def __init__(self, charger_id):
        # mqtt definitions
        self.mqtt_client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION1)
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
        self.mqtt_client.subscribe(f"{CHARGER_TOPIC}/{charger_id}")
        self.mqtt_client.loop_start()

        # stm definitions
        self.charger = ChargerLogic(charger_id, self)

        # driver
        self.stm_driver = stmpy.Driver()
        self.stm_driver.start(keep_active=True)
        self.stm_driver.add_machine(self.charger.stm)


    # Initial connected message
    def on_connect(self, client, userdata, flags, rc):
        print("MQTT Connected")

    # Battery percentage
    def on_message(self, client, userdata, msg):
        msg = json.loads(msg.payload)  # now a dict

        command = msg.get("command")

        print(f"charger {self.charger.charger_id} got a message.")

        if command == "start_charging":
            battery_target = msg.get("battery_target")
            car_id = msg.get("car_id")
            self.charger.battery_target = battery_target
            self.charger.car_id = car_id
            self.charger.stm.send("start_charging")

        # Handle stop_charging
        elif command == "stop_charging":
            print(f"Charging stopped for car {self.charger.car_id}")
            self.charger.stm.send("battery_charged")
        
        elif command == "battery_update":
            percentage = msg.get("percentage")
            self.charger.current_car_battery = percentage
            self.charger.stm.send("battery_update")
