# SenseHat runs on a different thread than the rest of the program. Be aware of this.
import threading
import time
from sense_hat import SenseHat

# Define colors here (R, G, B)
red = (255, 0, 0)
none = (0, 0, 0)

class ErrorHandler:
    def __init__(self):
        self.sense = SenseHat()
        self.isError = False
        self.error_thread = threading.Thread(target=self._loop)

    def start(self):
        self.isError = True
        if not self.error_thread.is_alive():
            self.error_thread.start()

    def stop(self):
        self.isError = False
        self.sense.clear()

    def _loop(self):
        while True:
            if self.isError:
                for y in range(8):
                    for x in range(8):
                        if (x == y) or (x + y == 7):  # Diagonal conditions for 'X'
                            self.sense.set_pixel(x, y, red[0], red[1], red[2])
                        else:
                            self.sense.set_pixel(x, y, none[0], none[1], none[2])
                time.sleep(0.5)
                self.sense.clear()
                time.sleep(0.5)
            else:
                time.sleep(1)