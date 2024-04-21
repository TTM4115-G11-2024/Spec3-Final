from appJar import gui
from datetime import datetime, timedelta
import requests, json, pytz  


class App(object):
    def __init__(self):
        self.car_id: str
        self.chosen_station: int
        self.chosen_percentage: int
        self.url = "http://127.0.0.1:8000/"

        self.app = gui()
        self.run()
        self.app.go()

    def run(self):
        self.app.addLabelEntry('Insert Car ID')
        self.app.setEntry('Insert Car ID', '#')
        self.app.addButton("Confirm ID", self.insert_CarID)

    def insert_CarID(self):
        self.car_id  = self.app.getEntry('Insert Car ID')
      
        if self.car_id:
            car_url = self.url + "cars/"

            self.params = {
                         "id": str(self.car_id)}
        
            r = requests.post(url=car_url, data=json.dumps(self.params))
    
            # Check if the request was successful (status code 200)
            if r.status_code == 200:
                # Extracting response text
                resp = r.json()
                print("Response is:%s" % resp)
            else:
                # Print error message if the request was not successful
                print("Error:", r.text)
            self.app.startSubWindow("Main_Window", modal=True)
            self.main_page()

    def main_page(self):
        self.app.addLabel("title_mp", 'Best Charger, Car "{}".'.format(self.car_id))
        self.app.addButton("Overview", self.overview)
        self.app.addButton("Charging", self.charging)
        self.app.addButton("Reservations", self.reservations)
        self.app.addButton("My page", self.mp)
        self.app.addButton("Close", self.close_program)
        self.app.stopSubWindow()
        self.app.hide()
        self.app.showSubWindow("Main_Window")

    def close_program(self):
        self.app.stop()
        
    def overview(self):    
        self.app.startSubWindow("Overview_Window", modal=True)
        self.app.addLabel("title_ow", 'Overview page')
        self.app.addLabel("charger_info", "Select Charger Info:")
        buttons = ["1", "2", "3", "4", "5", "6", "7", "8"]
        row = 2
        col = 0
        for button_name in buttons:
            self.app.addButton(button_name, lambda selected_station_info=button_name: self.selected_station(selected_station_info), row, col) 
            col += 1
            if col == 4:
                col = 0
                row += 1

        self.app.stopSubWindow()
        self.app.hide()
        self.app.showSubWindow("Overview_Window")
        
    def selected_station (self, selected_station_info):
        url_this_charger = self.url + "chargers/"+selected_station_info
        r = requests.get(url_this_charger)
        if r.status_code == 200:
            parsed = r.json()
            self.app.startSubWindow("Station_Window", modal=True)
            self.app.addLabel("title_station", "Station Information")
            self.app.addLabel("label_station_id", "Station ID:" + str(parsed["id"]))
            if parsed["is_available"]:
                self.app.addLabel("avaialble_now", "Avaialable Now")
            else:
                self.app.addLabel("unavaialble_now", "Currently Unavailable")
           
            # Stop the subwindow
            self.app.stopSubWindow()

            # Show the subwindow
            self.app.showSubWindow("Station_Window")



    def charging(self):   
        self.app.startSubWindow("Charging_Window", modal=True) 
        self.app.addLabel("title_ch", 'Charging page')

        self.app.addLabelEntry('Insert Station ID')
        self.app.setEntry('Insert Station ID', '')
        self.app.addLabelEntry('Insert Desired Charge')
        self.app.setEntry('Insert Desired Charge', '100%')
        self.app.addButton("Confirm charging", self.start_charging)

        self.app.stopSubWindow()
        self.app.hide()
        self.app.showSubWindow("Charging_Window")

        #http://appjar.info/outputWidgets/#label
        return "Hello"
    
    def start_charging(self):
        self.chosen_station  = self.app.getEntry('Insert Station ID')
        self.chosen_percentage = self.app.getEntry('Insert Desired Charge')
        chosen_percentage_int = int(self.chosen_percentage.rstrip('%'))
        charging_url = self.url + "chargers/"+str(self.chosen_station)+"/activate/"
        self.params = {
                        "car_id": str(self.car_id),
                        "target_percentage": chosen_percentage_int}
        
        print(self.params)
        
        r = requests.post(url=charging_url, data=json.dumps(self.params))
    
        # Check if the request was successful (status code 200)
        if r.status_code == 200:
            # Extracting response text
            resp = r.json()
            print("Response is:%s" % resp)
        else:
            # Print error message if the request was not successful
            print("Error:", r.text)
    
    def reservations(self):    
        self.app.startSubWindow("Reserve_Window", modal=True)
        self.app.addLabel("title_re", 'Reservation page')
        self.app.addLabelEntry('Insert Desired Charger')
        self.app.setEntry('Insert Desired Charger', '')
        self.app.addLabel("text_select_slot", 'Select 30 min slot:')
        upcoming_times = self.get_next_half_hour_times()

        row = 3
        col = 0
        for button_name in upcoming_times:
            self.app.addButton(button_name, lambda selected_time=button_name: self.reserve(selected_time), row, col)
            col += 1
            if col == 2:
                col = 0
                row += 1

        self.app.stopSubWindow()
        self.app.hide()
        self.app.showSubWindow("Reserve_Window")

    def mp():    
        return "Hello"
    
    def reserve(self, selected_time):
        charger = self.app.getEntry('Insert Desired Charger') 
        #NOT NAIVE  
        current_time = datetime.now(pytz.utc)

        selected_hour, selected_minute = map(int, selected_time.split(':'))
        start_time = current_time.replace(hour=selected_hour, minute=selected_minute, second=0, microsecond=0)
        end_time = start_time + timedelta(minutes=30)

         # Prepare request parameters
        params = {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "car_id": str(self.car_id),
            "charger_id": charger
        }

        # Make POST request to /reservations/
        p_url = "http://127.0.0.1:8000/reservations/"
        response = requests.post(p_url, json=params)

        if response.status_code == 200:
            print("Reservation successfully made.")
        else:
            print("Failed to make reservation. Error:", response.text)
   
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
