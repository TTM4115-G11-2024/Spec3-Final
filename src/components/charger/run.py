import time

import ipywidgets as widgets
import paho.mqtt.client as mqtt
from IPython.display import display
from sense_hat import SenseHat
from stmpy import Driver, Machine

current_battery_percentage = None


def on_message(client, message):
    info = message.payload.decode()

    if info.startswith("b"):  # NOTE: the battery must send 'bXX' as the MQTT msg
        battery = info[1:]
        #current_battery_percentage = int(number_part)
        return int(battery)
    elif info.startswith("car "): #NOTE: the battery is supposed to send: car XXXXXX connected
        carID = info[1:]
        return carID


#mqttBroker = "mqtt.eclipseprojects.io"
#client = mqtt.Client("Charger")
#client.connect(mqttBroker)

MQTT_BROKER = "test.mosquitto.org"
MQTT_PORT = 1883
MQTT_TOPIC = ["charger_percent", "ttm4115/g11/cars/"]

client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION1)
client.connect(MQTT_BROKER, MQTT_PORT)
client.loop_forever()
client.subscribe(MQTT_TOPIC)

client.on_message = on_message


sense = SenseHat()

r = 255
g = 0
b = 0

msleep = lambda x: time.sleep(x / 1000.0)

accped_users = {"Adrian": ["18:00", "20:00"], "Sindre": ["13:45"]}

reservation_time_and_battery = {"18:00": [67], "20:00": [55], "13:45": [44]}


class Charger:

    # # callback method, called by the button 'switch' when it is pressed
    # def on_value_change(self, change):
    #     if change['new']:
    #         self.stm.send('hand')
    #     else:
    #         self.stm.send('no_hand')

    # Connected nozzle, and need to authenticate user.
    def charger_nozzle_detected(self):
        print("connected")
        sense.clear([255, 165, 0])  # Sets screen to ORANGE.

    def charger_nozzle_disconnected(self):
        print("disconnected")

        # Sensehat: Blink GREEN screen for 5 seconds.
        for i in range(10):
            sense.clear([82, 100, 11])  # Sets screen to LIME YELLOW.
            time.sleep(0.5)
            sense.clear([0, 0, 0])  # Turn OFF screen.

        sense.clear([82, 100, 11])  # Set screen to LIME YELLOW.
        # self.idle

    def activate_charger(self, user, time): 
        if user in accped_users and time in accped_users[user]:
            print(f"charging until{reservation_time_and_battery[time]} or time is up")
            self.charged(user, time)
            self.charging
        else:
            print("user has no reserved timeslot")
            self.connected

    def display_two_digits(a_number):

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

        black = (0, 0, 0)
        color = (255, 255, 255)

        if a_number < 0:
            negative = True
            a_number = abs(a_number)
        else:
            negative = False

        first_digit = int(int(a_number / 10) % 10)
        second_digit = int(a_number % 10)

        # set pixels for the two digits
        pixels = [black for i in range(64)]
        digit_glyph = digits0_9[first_digit]
        for i in range(0, len(digit_glyph)):
            pixels[digit_glyph[i]] = color
        digit_glyph = digits0_9[second_digit]
        for i in range(0, len(digit_glyph)):
            pixels[digit_glyph[i] + 4] = color

        # set pixels for a minus sign for negatives
        if negative:
            pixels[56] = color
            pixels[57] = color
            pixels[58] = color

        # set bottom right pixel if number is more than 2 digits
        if a_number > 99:
            pixels[63] = color

        # display the result
        sense.set_pixels(pixels)

    # TODO: Not sure if "battery_status" should be a parameter like this or how we get it.
    def charging_status(self, battery_cap):
        battery_status = on_message(client, client.on_message) 
        #charger listens to MQTT messages and gets battery percentage from car
        print(f"battery status: {battery_status}")
        if battery_status == battery_cap:
            print("Done charging")
            # Activate the trigger "charged".
            self.mqtt_client.publish(MQTT_TOPIC, "charged")   #charger confirms the car it is fully charged
        else:
            # Activate the trigger "not_charged".

            # TODO 1: Read in Battery Status.

            # Clear screen.
            sense.clear([0, 0, 0])

            # Displays a two digit number on the SenseHat in WHITE.
            # display_two_digits(battery_status)

    def charged(self, user, time):
        print("time is up")
        print("done charging")

    def error_occur(self):
        print("error")

        # Sensehat: Display "X" in RED.
        red = (255, 0, 0)
        x_pattern = [
            red,
            0,
            0,
            0,
            0,
            0,
            0,
            red,
            0,
            red,
            0,
            0,
            0,
            0,
            red,
            0,
            0,
            0,
            red,
            0,
            0,
            red,
            0,
            0,
            0,
            0,
            0,
            red,
            red,
            0,
            0,
            0,
            0,
            0,
            0,
            red,
            red,
            0,
            0,
            0,
            0,
            0,
            red,
            0,
            0,
            red,
            0,
            0,
            0,
            red,
            0,
            0,
            0,
            0,
            red,
            0,
            red,
            0,
            0,
            0,
            0,
            0,
            0,
            red,
        ]
        sense.set_pixels(x_pattern)

    def error_resolved(self):
        print("resolved the error")

        # Sensehat: Blink GREEN screen for 5 seconds.
        for i in range(10):
            sense.clear([82, 100, 11])  # Sets screen to LIME YELLOW.
            time.sleep(0.5)
            sense.clear([0, 0, 0])  # Turn OFF screen.

        sense.clear([82, 100, 11])  # Set screen to LIME YELLOW.


init_to_idle = {
    "source": "init",
    "target": "idle",
}

idle_to_connected = {
    "source": "idle",
    "target": "connected",
    "effect": "charger_nozzle_detected; activate_charging",
}
connected_to_idle = {
    "source": "connected",
    "target": "idle",
    "effect": "charger_nozzle_disconnected",
}

connected_to_charging = {
    "trigger": "activate_charger",
    "source": "connected",
    "target": "charging",
    "effect": "TODO: start timer for the reserved time slot amount",
}

charging_to_charging = {
    "trigger": "not_charged",
    "source": "charging",
    "target": "charging",
    "effect": "charging_status",
}

charging_to_idle = {
    "trigger": "charged",
    "source": "charging",
    "target": "idle",
}


error_to_idle = {
    "trigger": "error_resolved",
    "source": "error",
    "target": "idle",
}
idle_to_error = {
    "trigger": "error_occur",
    "source": "idle",
    "target": "error",
}

connected_to_error = {
    "trigger": "error_occur",
    "source": "connected",
    "target": "error",
}

charging_to_error = {
    "trigger": "error_occur",
    "source": "charging",
    "target": "error",
}
charger = Charger()

charger_machine = Machine(
    transitions=[
        init_to_idle,
        idle_to_connected,
        connected_to_charging,
        connected_to_idle,
        charging_to_charging,
        charging_to_idle,
        error_to_idle,
        idle_to_error,
        charging_to_error,
        connected_to_error,
    ],
    obj=charger,
    name="charging_the_car",
)
driver = Driver()
driver.add_machine(charger_machine)
driver.start(max_transitions=12)
driver.stop()
