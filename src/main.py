import sys
import components.car.run as car
import components.charger.run as charger
import components.app.run as app
import components.server.run as server



def main():
    args = sys.argv
    if len(args) < 2:
        print("no args")
        exit()

    if args[1] == 'car':
        car.run()

    elif args[1] == 'charger':
        charger.run()
    
    elif args[1] == 'app':
        app.run()
    
    elif args[1] == 'server':
        server.run()
    else:
        print("command not found")


if __name__ == "__main__":
    main()