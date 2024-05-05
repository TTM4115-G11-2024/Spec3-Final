# Introduction
This project is done by Team 11 in the course TTM4115, the spring of 2024.

For context on the repository it's important to have read our System Specification 3 (course delivery).

# Running the Application
## Installation
### MacOS and Linux
Execute the following commands from the root directory:
```bash
python3.12 -m venv env
source env/bin/activate
pip install -r requirements.txt
```
### Windows
Execute the following commands from the root directory:
```bash
python3.12 -m venv env
source .\venv\Scripts\activate
pip install -r requirements.txt
```

## Running
First, activate the virtual environment with `source env/bin/activate` (Mac/Linux).

Each component has slightly different ways of being started:

### App
```
python src/components/app/run.py
```

### Car
```
python src/components/car/run.py <car_id>
```
The `car_id` can be any string, but remember the car needs to be registered in the server database for the component to work correctly.
This is done through the App user interface when prompted for a Car ID.

### Charger
NB! This component is supposed to be ran on a Raspberry Pi with sense_hat.
```
python src/components/charger/run.py <charger_id>
```
The `charger_id` can be any integer, but remember the charger needs to be registered in the server database for the component to work correctly.

This has to be done manually as it is a part of the charging station setup process, supposed to be performed by the charging station owner. However, by default, the server database will contain 8 chargers:
* The chargers with ID 1, 2, 3, 4 are *non-reservable* chargers.
* The chargers with ID 5, 6, 7, 8 are *reservable* chargers.


### Server
```
python src/components/server/run.py
```
# Raspberry Pi
## Information about the Pi
Hostname: raspberrypi

Username: g11

Password: seveneleven

- SSH should be activated and use Password above to authenticate.
- To connect to it use Mobile hotspot on your phone.
- Currently only Sindre's network "Sid" is available, you find this under available WiFi networks.
- ### The wifi information:
  * WIFI name: Sid
  * password: 1234567890
## Accessing the project:
Write this in the terminal:
```bash
ssh g11@raspberrypi.local
cd /home/g11/Projects/Spec3-Final/
```

# Using SenseHat to light up display
## Currently available lighting modes (state: description):
1) init: gray background
2) available: green background
3) unavailable: orange background
4) authenticating: "Authenticating..." shown from right to left.
5) battery status: Two digit number shown in white. When reached battery cap: Blink yellow -> (Batery_cap)% -> Blink yellow -> "Done..." from right to left.
6) error: Red X

## How to use the different SenseHat lighting modes in your code.
- Best advice: See test_sensehat.py
1) When charger program starts up, add the following:
```
import sensehat as SH

display = SH.Display(start_state) # By default use start_state = "init"
display.start()
```
2) Add the state of what to display on SenseHat in your code:
```
display.state = your_state # Remember to add this everytime you want to change the display to another one on the list above.
```
3) Give SenseHat information about the battery:
```
display.battery_cap = your_battery_cap
# Considering you are in charging state when this happens:
display.state = "battery status"
# Foreach time you read battery status from MQTT update the battery status on SenseHat:
display.battery = updated_battery_status
```
4) If there is an exit or terminate state/function for your program, add the function that terminates SenseHat too:
```
display.stop()
```
