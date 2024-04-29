from charger import ChargerComponent
import sys

def get_charger_id_arg():
    args = sys.argv
    if len(args) < 2:
        raise ValueError("charger_id is not specified. Run the program with: python run.py <charger_id>")
    
    charger_id = int(args[1])

    return charger_id

def run():
    charger_id = get_charger_id_arg()

    ChargerComponent(charger_id)

def run_from_python(charger_id):
    ChargerComponent(charger_id)


if __name__ == "__main__":
    run()
