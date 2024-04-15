# def run():
#     print("Hello from charger")
from stmpy import Machine, Driver
from IPython.display import display
import ipywidgets as widgets
import time
from sense_hat import SenseHat

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
        sense.clear([255, 165, 0]) # Sets screen to ORANGE.

    def charger_nozzle_disconnected(self):
        print("disconnected")

        # Sensehat: Blink GREEN screen for 5 seconds.
        for i in range(10):
            sense.clear([82, 100, 11]) # Sets screen to LIME YELLOW.
            time.sleep(0.5)
            sense.clear([0, 0, 0]) # Turn OFF screen.

        sense.clear([82, 100, 11]) # Set screen to LIME YELLOW.
        #self.idle

    def activate_charger(self, user, time):
        if user in accped_users and time in accped_users[user]:
            print(f"charging until{reservation_time_and_battery[time]} or time is up")
            self.charged(user, time)
            self.charging
        else:
            print("user has no reserved timeslot")
            self.connected

    def charged(self, user, time):
        print("time is up")
        print("done charging")
        self.idle

    def error_occur(self):
        print("error")

        # Sensehat: Display "X" in RED.
        red = (255, 0, 0)
        x_pattern = [
            red, 0, 0, 0, 0, 0, 0, red,
            0, red, 0, 0, 0, 0, red, 0,
            0, 0, red, 0, 0, red, 0, 0,
            0, 0, 0, red, red, 0, 0, 0,
            0, 0, 0, red, red, 0, 0, 0,
            0, 0, red, 0, 0, red, 0, 0,
            0, red, 0, 0, 0, 0, red, 0,
            red, 0, 0, 0, 0, 0, 0, red
        ]
        sense.set_pixels(x_pattern)

    def error_resolved(self):
        print("resolved the error")
        
        # Sensehat: Blink GREEN screen for 5 seconds.
        for i in range(10):
            sense.clear([82, 100, 11]) # Sets screen to LIME YELLOW.
            time.sleep(0.5)
            sense.clear([0, 0, 0]) # Turn OFF screen.

        sense.clear([82, 100, 11]) # Set screen to LIME YELLOW.

init_to_idle = {
    "source": "init",
    "target": "idle",
}

idle_to_connected = {
    "source": "idle",
    "target": "connected",
    "effect": "charger_nozzle_detected",
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
driver.start(max_transitions=10)
driver.stop()
