import threading
import time
from sense_hat import SenseHat

sense = SenseHat()
none = (0, 0, 0)
red = (255, 0, 0)
green = (0, 255, 0)
yellow = (255, 255, 0)
lime_yellow = (208, 254, 29)
orange = (255, 165, 0)
white = (255, 255, 255)

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

battery_level = 87
battery_cap = 90

while battery_level <= battery_cap:
    

    color = white
    if battery_level >= battery_cap:
        msg = str(battery_level) + "%"
        sense.show_message(msg, text_colour=color, back_colour=none)
        time.sleep(0.25)
        sense.clear(color)
        time.sleep(0.5)
        sense.show_message("Done", text_colour=color, back_colour=none)
        time.sleep(0.25)
        sense.clear(color)
    else:
        display_two_digits(battery_level)
        time.sleep(0.1)
    
    time.sleep(0.5)
    if battery_level != battery_cap:
        battery_level += 1
