import json
import paho.mqtt.client as mqtt
import stmpy
#import audio
import requests
import sensehat as SH
import time



# Configure the MQTT settings
MQTT_BROKER = "test.mosquitto.org"
MQTT_PORT = 1883
CHARGER_TOPIC = "ttm4115/g11/chargers"
CAR_TOPIC = "ttm4115/g11/cars"

# Server settings
SERVER_URL = "http://rnzco-2001-700-300-4015-6570-42-ebcd-44ec.a.free.pinggy.link"


# State machine logic for the Charger
class ChargerLogic:
    def __init__(self, charger_id, component):
        self.display = SH.Display("init")
        self.display.start()

        self.component : ChargerComponent = component
        self.charger_id : int = charger_id

        transitions = [
            {"source": "initial", "target": "idle", "effect": "stm_init"},
            {"trigger": "nozzle_connected", "source": "idle", "target": "connected", "effect": "on_nozzle_connected"},
            {"trigger": "nozzle_disconnected", "source": "connected", "target": "idle", "effect": "on_nozzle_disconnected"},
            {"trigger": "start_charging", "source": "connected", "target": "charging", "effect": "on_start_charging"},
            #{"trigger": "start_charging", "source": "idle", "target": "idle", "effect": "on_attempt_start_charging"}
            {"trigger": "battery_charged", "source": "charging", "target": "connected","effect": "on_battery_charged"}, # should target be idle or connected?
            {"trigger": "charging_timer",  "source": "charging", "target": "connected", "effect": "on_battery_charged"}, # should target be idle or connected?
            {"trigger": "battery_update", "source": "charging", "target": "charging", "effect": "on_battery_update"},
            # Error transitions
            {"trigger": "error", "source": "charging", "target": "error","effect": "on_error_occur"},
            {"trigger": "error", "source": "connected", "target": "error", "effect": "on_error_occur"},
            {"trigger": "resolved", "source": "error", "target": "idle", "effect": "on_error_resolved"},
            {"trigger": "hw_failure", "source": "error", "target": None, "effect": "on_hardware_failure"}
        ]

        states = [
            {"name": "charging", "exit": "stop_timer('charging_timer')"}
        ]

        self.stm = stmpy.Machine(name=f"{self.charger_id}", transitions=transitions, states=states, obj=self)

        # other variables
        self.car_id = None
        self.battery_target = 0
        self.current_car_battery = 0
        self.max_charging_time = 60 * 30 * 1000

    def stm_init(self):
        self.display.state = "available"
        self.display.battery_cap = 0

        self._deactivate_charger_in_server()
        self.stm.send("nozzle_connected") # for now nozzle is automatically connected
    
    def on_battery_update(self):
        self.display.battery = self.current_car_battery
        # Check if battery level reached
        if self.current_car_battery >= self.battery_target:
            self.stm.send("battery_charged")
            print(f"Received battery update: {self.current_car_battery}%. Charging stopped.")
        else:
            # display the charging percentage on sense hat
            self.display.state = "battery status"
            print()
            print(f"Received battery update: {self.current_car_battery}%. Charging continues.")
            pass


    def on_nozzle_connected(self):
        self.display.state = "unavailable"
        print("Charger plugged to car.")   


    def on_nozzle_disconnected(self):
        self.display.state = "available"
        print("Charger unplugged from car.")


    def on_start_charging(self):
        self.display.battery_cap = self.battery_target
        print(f"Charging started for car {self.car_id} with target {self.battery_target}%")
        # send start charging to car
        topic = f"{CAR_TOPIC}/{self.car_id}"
        payload = {
            "command": "start_charging",
            "charger_id": self.charger_id,
        }
        payload = json.dumps(payload)
        self.component.mqtt_client.publish(topic, payload)
#        audio.play_charging_started_sound()


    def on_battery_charged(self):
        print(f"Charging stopped for the car {self.car_id}")
        print("Battery target after done: " + str(self.battery_target))
        self.display.state = "battery charged"
        # send stop charging signal to car
        topic = f"{CAR_TOPIC}/{self.car_id}"
        payload = {"command": "stop_charging"}
        payload = json.dumps(payload)
        self.component.mqtt_client.publish(topic, payload)

        self.make_charger_available()
        self.car_id = None
        self.battery_target = 0
        self.current_car_battery = 0
#        audio.play_charging_completed_sound()
        

    def on_error_occur(self):
        self.display.state = "error"
        print("Error occurred")
        # error_handler.start()

    def on_error_resolved(self):
        self.display.state = "available"
        print("Error resolved")


    def on_hardware_failure(self):
        self.display.state = "error"
        print("Hardware failure detected. Shutting down.")

    
    def make_charger_available(self):
        self._deactivate_charger_in_server()
    
    def _deactivate_charger_in_server(self):
        url = f"{SERVER_URL}/chargers/{self.charger_id}/deactivate/"
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
            max_charging_time = msg.get("max_charging_time")
            self.charger.battery_target = battery_target
            self.charger.car_id = car_id
            self.charger.max_charging_time = max_charging_time
            self.charger.stm.send("start_charging")
            self.charger.stm.start_timer("charging_timer", max_charging_time * 1000)
            print(f"max_charging_time: {max_charging_time}")

        # Handle stop_charging
        elif command == "stop_charging":
            self.charger.stm.send("battery_charged")
        
        elif command == "battery_update":
            percentage = msg.get("percentage")
            self.charger.current_car_battery = percentage
            self.charger.stm.send("battery_update")
