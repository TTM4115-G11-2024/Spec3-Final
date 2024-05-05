from sense_hat import SenseHat
#import sensehat as SH
from time import sleep
# Define the functions

sense = SenseHat()

def red():
  sense.clear(255, 0, 0)

def blue():
  sense.clear(0, 0, 255)

connected = False

def nozzle(event):
    global connected
    if event.action != 'pressed':
        return
    if (not connected):
        connected = True
        print("red")
        return red()
    else:
        connected = False
        print("blue")
        return blue()

sense.stick.direction_middle = nozzle

# Tell the program which function to associate with which direction



    
while True:
  pass  # This keeps the program running to receive joystick events