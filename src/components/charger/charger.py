import threading
import json
import paho.mqtt.client as mqtt
import stmpy
#import audio
import requests
#import sensehat as SH
from sense_hat import SenseHat
import time

# Configure the MQTT settings 
MQTT_BROKER = "test.mosquitto.org"

MQTT_PORT = 1883
CHARGER_TOPIC = "ttm4115/g11/chargers"
CAR_TOPIC = "ttm4115/g11/cars"

# Server settings
SERVER_URL = "http://rnzzm-2001-700-300-4015-6570-42-ebcd-44ec.a.free.pinggy.link"


'''
NOTE: The 'self.interface.state' variable used in the code,
is not actually a part of the state machine logic.
It is the most convinent way to do the
threading functionality in sensehat.py.
'''

# State machine logic for the Charger
class ChargerLogic:
    def __init__(self, charger_id, component):

        self.component : ChargerComponent = component
        self.charger_id : int = charger_id

        # The triggers "nozzle_connceted" and "nozzle_disconnected" is triggered from SenseHat joystick middle-button press.
        # See sensehat.py for more details.
        transitions = [
            {"source": "initial", "target": "idle", "effect": "stm_init"},
            {"trigger": "nozzle_connected", "source": "idle", "target": "connected", "effect": "on_nozzle_connected"},
            {"trigger": "nozzle_disconnected", "source": "connected", "target": "idle", "effect": "on_nozzle_disconnected"},
            {"trigger": "start_charging", "source": "connected", "target": "charging", "effect": "stop_timer('charging_timer');on_start_charging"},
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

        self.stm = stmpy.Machine(name=f"{self.charger_id}", transitions=transitions, obj=self)

        self.interface = ChargerInterface("init", self.stm)
        self.interface.start()

        # other variables
        self.car_id = None
        self.battery_target = None
        self.current_car_battery = None
        self.max_charging_time = 60 * 30 * 1000

    def stm_init(self):
        self.interface.state = "available"
        self.interface.battery_cap = 0
        self._deactivate_charger_in_server() # Comment out this to test the code without server set up.
    
    def on_battery_update(self):
        self.interface.battery_lvl = self.current_car_battery
        # Check if battery level reached
        if self.current_car_battery >= self.battery_target:
            self.stm.send("battery_charged")
            print(f"Received battery update: {self.current_car_battery}%. Charging stopped.")
        else:
            # display the charging percentage on sense hat
            self.interface.state = "battery status"
            print(f"Received battery update: {self.current_car_battery}%. Charging continues.")
            pass


    def on_nozzle_connected(self):
        self.interface.state = "unavailable"
        print("Charger plugged to car.")   


    def on_nozzle_disconnected(self):
        self.interface.state = "available"
        print("Charger unplugged from car.")


    def on_start_charging(self):
        self.interface.battery_cap = self.battery_target

        print(f"Charging started for car {self.car_id} with target {self.battery_target}%")
        self.stm.start_timer("charging_timer", self.max_charging_time)
        print(f"Started charging_timer with {self.max_charging_time/1000}s")

        # send start charging to car
        topic = f"{CAR_TOPIC}/{self.car_id}"
        payload = {
            "command": "start_charging",
            "charger_id": self.charger_id,
        }
        payload = json.dumps(payload)
        self.component.mqtt_client.publish(topic, payload)

        #audio.play_charging_started_sound()


    def on_battery_charged(self):
        print(f"Charging stopped for the car {self.car_id}")
        
        self.interface.state = "battery charged"

        # send stop charging signal to car
        topic = f"{CAR_TOPIC}/{self.car_id}"
        payload = {"command": "stop_charging"}
        payload = json.dumps(payload)
        self.component.mqtt_client.publish(topic, payload)

        self.make_charger_available()
        self.car_id = None
        self.battery_target = 0
        self.current_car_battery = 0
        #audio.play_charging_completed_sound()
        

    def on_error_occur(self):
        self.interface.state = "error"
        print("Error occurred")

    def on_error_resolved(self):
        self.interface.state = "available"
        print("Error resolved")


    def on_hardware_failure(self):
        self.interface.state = "error"
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
            self.charger.max_charging_time = max_charging_time * 1000
            
            self.charger.stm.send("start_charging")
            
            
            print(f"max_charging_time: {max_charging_time}")

        # Handle stop_charging
        elif command == "stop_charging":
            self.charger.stm.send("battery_charged")
        
        elif command == "battery_update":
            percentage = msg.get("percentage")
            self.charger.current_car_battery = percentage
            self.charger.stm.send("battery_update")



# Define colors here (R, G, B)
COLORS = {
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "orange": (255, 165, 0),
    "yellow": (255, 255, 0),
    "none": (0, 0, 0),
    "white": (255, 255, 255),
}


# Constants for display_two_digits method
PIXEL_COUNT = 64
NEGATIVE_SIGN_START = 56
NEGATIVE_SIGN_END = 58
OVERFLOW_PIXEL = 63


class ChargerInterface:
    def __init__(self, state, stm):
        print("Charger interface: Initializing")
        self.sense = SenseHat()
        self.running = False
        
        # Display
        self.state = state
        self.battery_lvl = 0
        self.battery_cap = 0   
        self.wait = 1 # Default time for a state to be kept stable, so the user see it has been in this state.
        self.sense.clear(50, 50, 50) # Color is light gray.

        # Used as a pseudo state machine, due to threading needed. 
        # It is the most convenient way to implement the logic. 
        self.state_methods = {
            "init": self.init,
            "error": self.error,
            "available": self.available,    
            "unavailable": self.unavailable,    
            "battery status": self.battery_status,
            "battery charged": self.battery_charged,
            "authenticating": self.authenticating,
        }

        # Joystick (on_click callback function called)
        self.connected = False
        self.sense.stick.direction_middle = self.nozzle
        
        # Connet to the Charger's state machine
        self.stm = stm

        
    # Starting the thread
    def start(self):
        print("Charger interface: Starting thread")
        self.running = True
        self.display_thread = threading.Thread(target=self._loop)
        self.display_thread.start()
        print("Charger interface: Started")

    # Stopping the thread
    def stop(self):
        print("Charger interface: Stopping thread")
        self.running = False
        self.sense.clear()
        if self.display_thread:
            self.display_thread.join()
        print("Charger interface: Stopped")

    def display_two_digits(self, a_number, color):

        self.a_number = a_number

        # Digit patterns
        digits0_9 = [
            [2, 9, 11, 17, 19, 25, 27, 33, 35, 42],  # 0
            [2, 9, 10, 18, 26, 34, 41, 42, 43],  # 1
            [2, 9, 11, 19, 26, 33, 41, 42, 43],  # 2
            [1, 2, 11, 18, 27, 35, 41, 42],  # 3
            [3, 10, 11, 17, 19, 25, 26, 27, 35, 43],  # 4
            [1, 2, 3, 9, 17, 18, 27, 35, 41, 42],  # 5
            [2, 3, 9, 17, 18, 25, 27, 33, 35, 42],  # 6
            [1, 2, 3, 9, 11, 19, 26, 34, 42],  # 7
            [2, 9, 11, 18, 25, 27, 33, 35, 42],  # 8
            [2, 9, 11, 17, 19, 26, 27, 35, 43],  # 9
        ]

        black = COLORS["none"]

        if self.a_number < 0:
            negative = True
            self.a_number = abs(self.a_number)
        else:
            negative = False

        first_digit = int(int(self.a_number / 10) % 10)
        second_digit = int(self.a_number % 10)

        # set pixels for the two digits
        pixels = [black for i in range(PIXEL_COUNT)]
        digit_glyph = digits0_9[first_digit]
        for i, digit in enumerate(digit_glyph):
            pixels[digit] = color
        digit_glyph = digits0_9[second_digit]
        for i, digit in enumerate(digit_glyph):
            pixels[digit + 4] = color

        # set pixels for a minus sign for negatives
        if negative:
            pixels[NEGATIVE_SIGN_START] = color
            pixels[NEGATIVE_SIGN_START + 1] = color
            pixels[NEGATIVE_SIGN_END] = color

            

        # set bottom right pixel if number is more than 2 digits
        if self.a_number > 99:
            pixels[OVERFLOW_PIXEL] = color

        # display the result
        self.sense.set_pixels(pixels)


    def _loop(self):
        while self.running:
            method = self.state_methods.get(self.state)
            if method:
                method()
            else:
                break  
        
    
    def init(self):
        #message = "Sensehat is Starting up..."
        #print(message)
        #self.sense.show_message(message, text_colour=white, back_colour=COLORS["none"])
        return

    # Display a red "X".
    def error(self):
        for y in range(8):
            for x in range(8):
                if (x == y) or (x + y == 7):  # Diagonal conditions for 'X'
                    self.sense.set_pixel(x, y, COLORS["red"][0], COLORS["red"][1], COLORS["red"][2])
                else:
                    self.sense.set_pixel(x, y, COLORS["none"][0], COLORS["none"][1], COLORS["none"][2])  
        time.sleep(self.wait) # Keep it stable for some time, so the user see it has been in this state.

    def available(self):
        self.sense.clear(COLORS["green"])
        time.sleep(1) # Keep it stable for some time, so the user see it has been in this state.

    def unavailable(self):
        self.sense.clear(COLORS["orange"])
        time.sleep(self.wait) # Keep it stable for some time, so the user see it has been in this state.

    def battery_charged(self):
        self.sense.clear(COLORS["orange"])
        time.sleep(1)
        message = str(self.battery_cap) + "%"
        self.sense.show_message(message, text_colour=COLORS["orange"], back_colour=COLORS["none"])
        self.sense.clear(COLORS["orange"])
        time.sleep(1)
        message = "Done"
        self.sense.show_message(message, text_colour=COLORS["orange"], back_colour=COLORS["none"])


    def battery_status(self):
        self.display_two_digits(self.battery_lvl, COLORS["white"])
        # Allow time for the display to show the correct value.
        time.sleep(0.5)
      
    def authenticating(self):
        self.sense.show_message("Authenticating...", text_colour=COLORS["orange"], back_colour=COLORS["none"])
        time.sleep(self.wait) # Keep it stable for some time, so the user see it has been in this state. 

    # Callback function for middle joystick button to set Connected/Disconnected Nozzle.
    def nozzle(self, event):
        if event.action != 'pressed':
            return
    
        # When nozzle is connected
        if (self.connected): 

            #self.sense.clear(COLORS["red"]) # Example usage

            # TODO: Send the "connected" message here.
            self.stm.send("nozzle_disconnected")

            self.connected = False
            #print("Charger Nozzle: Disconnected")
            
        # When nozzle is disconnected.
        else:
            # TODO: Send the "disconnected" message here.
            self.stm.send("nozzle_connected")
            
            self.connected = True
            #print("Charger Nozzle: Connected")

    
    