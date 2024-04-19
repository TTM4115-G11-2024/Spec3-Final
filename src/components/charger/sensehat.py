# SenseHat runs on a different thread than the rest of the program. Be aware of this.
import threading
import time
from sense_hat import SenseHat

# Define colors here (R, G, B)
red = (255, 0, 0)
green = (0, 255, 0)
orange = (255, 165, 0)
none = (0, 0, 0)



class Display:
    def __init__(self, state, battery_level):
        self.sense = SenseHat()
        self.running = False
        self.state = state.lower()
        self.battery = battery_level    
        
    def start(self):
        self.running = True
        self.display_thread = threading.Thread(target=self._loop)
        self.display_thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()

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
            self.sense.clear()

            if self.state == "error":
                self.error()
            elif self.state == "available":
                
            elif self.state == "unavailable":

            elif self.state == "battery status":

            elif self.state == "authenticating":

            
                
            else:
                print("ERROR: Invalid state input.")
            

    def error(self):
        for y in range(8):
            for x in range(8):
                if (x == y) or (x + y == 7):  # Diagonal conditions for 'X'
                    self.sense.set_pixel(x, y, red[0], red[1], red[2])
                else:
                    self.sense.set_pixel(x, y, none[0], none[1], none[2])
        time.sleep(0.5)
        self.sense.clear()
        time.sleep(0.5)      

    def available(self):
        self.sense.clear(green)
        time.sleep(0.5)

    def unavailable(self):
        self.sense.clear(orange)
        time.sleep(0.5)

    def battery_status(self, battery_cap, battery_lvl):
        self.battery_cap = battery_cap
        self.battery_lvl = battery_lvl

        

        message = str(self.battery) + "%"
        self.sense.show_message(message, text_colour=none, back_colour=none)
        time.sleep(0.5)

    def authenticating(self):
        self.sense.show_message("A", text_colour=none, back_colour=none)
        time.sleep(0.5)