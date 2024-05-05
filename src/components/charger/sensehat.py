# SenseHat runs on a different thread than the rest of the program. Be aware of this.
import threading
import time
import paho.mqtt.client as mqtt
from sense_hat import SenseHat

# TODO: Set up the mqtt for message passing.


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


class Display:
    def __init__(self, state):
        print("Charger display: Initializing")
        self.sense = SenseHat()
        self.running = False
        
        # Display
        self.state = state
        self.battery_lvl = 0
        self.battery_cap = 0   
        self.wait = 1   # Default time for a state to be kept stable, so the user see it has been in this state.
        self.sense.clear(50, 50, 50)    # Color is light gray.

        self.state_methods = {
            "init": self.init,
            "error": self.error,
            "available": self.available,    
            "unavailable": self.unavailable,    
            "battery status": self.battery_status,
            "battery charged": self.battery_charged,
            "authenticating": self.authenticating,
        }

        # Joystick
        self.connected = False
        self.sense.stick.direction_middle = self.nozzle

        # MQTT

        
    # Starting the thread
    def start(self):
        print("Charger display: Starting thread")
        self.running = True
        self.display_thread = threading.Thread(target=self._loop)
        self.display_thread.start()
        print("Charger display: Started")

    # Stopping the thread
    def stop(self):
        print("Charger display: Stopping thread")
        self.running = False
        self.sense.clear()
        if self.display_thread:
            self.display_thread.join()
        print("Charger display: Stopped")

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

    def nozzle(self, event):
        if event.action != 'pressed':
            return
    
        # When nozzle is connected
        if (self.connected): 

            #self.sense.clear(COLORS["red"]) # Example usage

            # TODO: Send the "connected" message here.
            self.stm.send("nozzle_disconnected")

            self.connected = False
            print("Charger Nozzle: Disconnected")
            
        # When nozzle is disconnected.
        else:
            # TODO: Send the "disconnected" message here.
            self.stm.send("nozzle_connected")
            self.connected = True
            print("Charger Nozzle: Connected")

    
    