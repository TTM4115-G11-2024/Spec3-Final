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
## Currently available lighting modes:
1) Red X for Error state. Instance: ErrorHandler()
2) TBD...
## How to use the different SenseHat lighting modes in your code.
* Create an instance of the class in sensehat.py
* Code has the following format: (see test_sensehat.py for examples)
```
instance = Instance()

# Start instance: Add this where you want to enable the SenseHat to display the desired output.
instance.start()

# Do other tasks...
time.sleep(2)

# Stop instance: This function must be called when you want to stop displaying SenseHat display started by instance.start().
instance.stop()

```
