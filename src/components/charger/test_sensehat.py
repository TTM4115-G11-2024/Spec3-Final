import sensehat as SH
import time

# This file shows how to enable the SenseHat display.

# ErrorHandler
def test_error_handler():
    # Create an instance of ErrorHandler
    error_handler = SH.ErrorHandler()

    # Start error
    error_handler.start()
    
    # Do other tasks...
    time.sleep(2)
    
    # Stop error
    error_handler.stop()



test_error_handler()
