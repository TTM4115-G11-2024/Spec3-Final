# def run():
#     print("Hello from charger")
from stmpy import Machine, Driver
from IPython.display import display
import ipywidgets as widgets

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
        # TODO 1: Sensehat: Display ORANGE screen.

    def charger_nozzle_disconnected(self):
        print("disconnected")
        # TODO 1: Sensehat: Blink GREEN screen for 5 seconds.
        # TODO 2: Sensehat: Display GREEN screen
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
        # TODO 1: Sensehat: Display "X" in RED.

    def error_resolved(self):
        print("resolved the error")
        # TODO 1: Sensehat: Display GREEN screen

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
