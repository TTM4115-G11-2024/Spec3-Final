# Raspberry Pi
## Information about the Pi
Hostname: raspberrypi

Username: g11

Password: seveneleven

- SSH should be activated and use Password above to authenticate.
- To connect to it use Mobile hotspot on your phone.
- Currently only Sindre's network "Sid" is available, you find this under available WiFi networks.
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
* Create an instance of the class in sensehat.py
* Run the following code
```
instance = Instance()

# Start error
instance.start()

# Do other tasks...
time.sleep(2)

# Stop error
instance.stop()

```
* Example can be seen in test_sensehat.py.
