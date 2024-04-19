import sensehat as SH
import time

# This file shows how to enable the SenseHat display.

# ErrorHandler
## Create an instance of ErrorHandler
error_handler = SH.ErrorHandler()

# Start error
error_handler.start()

# Do other tasks...
time.sleep(2)

# Stop error
error_handler.stop()
## End ErrorHandler

