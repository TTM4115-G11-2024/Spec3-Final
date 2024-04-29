
import sensehat as SH
import time


# Example of hos to use the SenseHat functions made to display the charger states.
def test_sensehat():
    # An instance of the sensehat that starts in the state "init". Can start in other states too.
    display = SH.Display("init")
    print(display.state)
    # Start error
    display.start()
    
    # Do other tasks...
    time.sleep(2)
    
    display.state = "available"
    print(display.state)
    time.sleep(5)
    
    display.state = "unavailable"
    print(display.state)
    time.sleep(2)

    display.battery_cap = 5
    display.state = "battery status"
    print(display.state)
    for i in range(0, display.battery_cap + 1, 1):
        display.battery = i
        time.sleep(1)
    time.sleep(5)
    
    display.state = "available"
    print(display.state)
    time.sleep(2)
    

    display.state = "error"
    print(display.state)
    time.sleep(3)
    
    display.state = "available"
    print(display.state)
    time.sleep(5)

    # Remember to stop on exit, as this is a safe way to terminate the sensehat program.
    display.stop()


# The function that runs the test.
test_sensehat()
