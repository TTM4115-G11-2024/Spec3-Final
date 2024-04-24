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
Activate the virtual environment with `source env/bin/activate` (Mac/Linux).
Run the application with:
```
python src/main.py <component-name>
```

The attribute `component-name`can be one of the following:
* `car`
* `charger`
* `app`
* `server`

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

display = SH.Display(start_state)
display.start()
```
2) Add the state of what to display on SenseHat in your code:
```
display.state = your_state
```
3) Give SenseHat information about the battery:
```
# Considering you are in charging state when this happens:
display.state = "battery status"

display.battery_cap = your_battery_cap
# Foreach time you read battery status from MQTT update the battery status on SenseHat:
display.battery = updated_battery_status
```
4) If there is an exit or terminate state/function for your program, add the function that terminates SenseHat too:
```
display.stop()
```
