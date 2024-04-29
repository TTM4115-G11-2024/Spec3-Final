# SenseHat runs on a different thread than the rest of the program. Be aware of this.
import threading
import time
from sense_hat import SenseHat

# Define colors here (R, G, B)
red = (255, 0, 0)
green = (0, 255, 0)
orange = (255, 165, 0)
yellow = (255, 255, 0)
none = (0, 0, 0)
white = (255, 255, 255)



class Display:
    def __init__(self, state):
        print("SenseHat being initialized.")
        self.sense = SenseHat()
        self.running = False
        self.state = state
        self.battery = 0
        self.battery_cap = 0   
        self.wait = 1
        self.sense.clear(50, 50, 50)
        
    def start(self):
        print("SenseHat has started running.")
        self.running = True
        self.display_thread = threading.Thread(target=self._loop)
        self.display_thread.start()

    def stop(self):
        print("SenseHat has stopped running.")
        self.running = False
        self.sense.clear()
        if self.display_thread:
            self.display_thread.join()

    def set_battery_level(self, battery_level):
        self.battery = battery_level
    
    def set_state(self, state):
        self.state = state

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

        black = none

        if self.a_number < 0:
            negative = True
            self.a_number = abs(self.a_number)
        else:
            negative = False

        first_digit = int(int(self.a_number / 10) % 10)
        second_digit = int(self.a_number % 10)

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
        if self.a_number > 99:
            pixels[63] = color

        # display the result
        self.sense.set_pixels(pixels)

    def _loop(self):
        while self.running:
            if self.state == "init":
                self.init()
            elif self.state == "error":
                self.error()
            elif self.state == "available":
                self.available()
            elif self.state == "unavailable":
                self.unavailable()
            elif self.state == "battery status":
                self.battery_status()
            elif self.state == "battery charged":
                self.battery_charged()
            elif self.state == "authenticating":
                self.authenticating()
            elif self.state == "clear":
                self.sense.clear()
            else:
                break   
        
    
    def init(self):
        #message = "Sensehat is Starting up..."
        #print(message)
        #self.sense.show_message(message, text_colour=white, back_colour=none)
        return

    
    def error(self):
        for y in range(8):
            for x in range(8):
                if (x == y) or (x + y == 7):  # Diagonal conditions for 'X'
                    self.sense.set_pixel(x, y, red[0], red[1], red[2])
                else:
                    self.sense.set_pixel(x, y, none[0], none[1], none[2])  
        time.sleep(self.wait) # Keep it stable for some time, so the user see it has been in this state.

    
    def available(self):
        self.sense.clear(green)
        time.sleep(1) # Keep it stable for some time, so the user see it has been in this state.

    
    def unavailable(self):
        self.sense.clear(orange)
        time.sleep(self.wait) # Keep it stable for some time, so the user see it has been in this state.

    def battery_charged(self):
        self.sense.clear(yellow)
        time.sleep(1)
        message = str(self.battery_cap) + "%"
        self.sense.show_message(message, text_colour=yellow, back_colour=none)
        self.sense.clear(yellow)
        time.sleep(1)
        message = "Done"
        self.sense.show_message(message, text_colour=yellow, back_colour=none)


    def battery_status(self):
        self.display_two_digits(self.battery, white)
        # Allow time for the display to show the correct value.
        time.sleep(0.5)
      
    def authenticating(self):
        self.sense.show_message("Authenticating...", text_colour=orange, back_colour=none)
        time.sleep(self.wait) # Keep it stable for some time, so the user see it has been in this state. 
