from car import BatteryComponent
import sys

def get_car_id_arg():
    args = sys.argv
    if len(args) < 2:
        raise ValueError("car_id is not specified. Run the program with: python run.py <car_id>")
    
    car_id = args[1]

    return car_id

def run():
    car_id = get_car_id_arg()

    BatteryComponent(car_id)

def run_from_python(car_id):
    BatteryComponent(car_id)


if __name__ == "__main__":
    run()
