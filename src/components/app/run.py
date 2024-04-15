from appJar import gui
from datetime import datetime, timedelta


class App(object):
    def __init__(self):
        self.car_id = None
        self.app = gui()
        self.run()
        self.app.go()

    def run(self):
        self.app.addLabelEntry('Insert Car ID')
        self.app.setEntry('Insert Car ID', '#')
        self.app.addButton("Confirm ID", self.insert_CarID)
        #return "Hello from mobile-app"

    def insert_CarID(self, title):
        print('Button with title "{}" pressed!'.format(title))
        ID = self.app.getEntry('Insert Car ID')
        self.car_id = ID
        print('And the current text field shows "{}".'.format(ID))
        if ID:
            self.app.startSubWindow("Main_Window", modal=True)
            self.main_page()

    def main_page(self):
        self.app.addLabel("title_mp", 'Best Charger, Car "{}".'.format(self.car_id))
        self.app.addButton("Overview", self.overview)
        self.app.addButton("Charging", self.charging)
        self.app.addButton("Reservations", self.reservations)
        self.app.addButton("My page", self.mp)
        self.app.stopSubWindow()
        self.app.hide()
        self.app.showSubWindow("Main_Window")
        
    def overview(self):    
        self.app.startSubWindow("Overview_Window", modal=True)
        self.app.addLabel("title_ow", 'Overview page')
        buttons = ["Station 1", "Station 2", "Station 3", "Station 4",
           "Station 5", "Station 6", "Station 7", "Station 8"]
        row = 1
        col = 0
        for button_name in buttons:
            self.app.addButton(button_name, self.press, row, col) #remember to change press
            col += 1
            if col == 4:
                col = 0
                row += 1

        self.app.stopSubWindow()
        self.app.hide()
        self.app.showSubWindow("Overview_Window")
        return "Hello"

    def charging(self):   
        self.app.startSubWindow("Charging_Window", modal=True) 
        self.app.addLabel("title_ch", 'Charging page')

        self.app.addLabelEntry('Insert Station ID')
        self.app.setEntry('Insert Station ID', '#')
        self.app.addLabelEntry('Insert Desired Charge')
        self.app.setEntry('Insert Desired Charge', '100%')
        self.app.addButton("Confirm charging", self.start_charging)

        self.app.stopSubWindow()
        self.app.hide()
        self.app.showSubWindow("Charging_Window")

        #http://appjar.info/outputWidgets/#label
        return "Hello"
    
    def start_charging(self):
        return "Hello"
    
    def reservations(self):    
        self.app.startSubWindow("Reserve_Window", modal=True)
        self.app.addLabel("title_re", 'Reservation page')
        self.app.addLabel("text_select_slot", 'Select 30 min slot:')
        upcoming_times = self.get_next_half_hour_times()

        row = 2
        col = 0
        for button_name in upcoming_times:
            self.app.addButton(button_name, self.press, row, col) #remember to change press
            col += 1
            if col == 2:
                col = 0
                row += 1

        self.app.stopSubWindow()
        self.app.hide()
        self.app.showSubWindow("Reserve_Window")
        return "Hello"

    def mp():    
        return "Hello"
    
    def press():
        return "Hello"

    def get_next_half_hour_times(self):
        current_time = datetime.now()
        current_minute = current_time.minute
        if current_minute < 30:
            next_half_hour = current_time.replace(minute=30, second=0, microsecond=0)
        else:
            next_half_hour = current_time.replace(hour=current_time.hour + 1, minute=0, second=0, microsecond=0)
        
        times = []

        # Add the next half-hour increment after the current time
        times.append(next_half_hour.strftime("%H:%M"))

        # Add the subsequent half-hour increments
        for _ in range(3):
            next_half_hour += timedelta(minutes=30)
            times.append(next_half_hour.strftime("%H:%M"))

        return times




App()
