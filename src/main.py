import sys
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path + "/components/app")
sys.path.append(dir_path + "/components/car")
sys.path.append(dir_path + "/components/charger")
sys.path.append(dir_path + "/components/server")

import components.app.run as app
import components.car.run as car
import components.charger.run as charger
import components.server.run as server

import threading


t = threading.Thread(target=server.run, name="server")
t.start()

num_chargers = 8
for i in range(1, num_chargers + 1):
    t = threading.Thread(target=charger.run_from_python, name="charger" + str(i), args=(i,))
    t.start()

num_cars = 10
for i in range(1, num_cars + 1):
    car_id = "C" + str(i)
    print(car_id)
    t = threading.Thread(target=car.run_from_python, name="car" + str(i), args=(car_id,))
    t.start()


print("hi")