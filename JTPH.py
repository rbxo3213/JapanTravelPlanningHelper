import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import tkcalendar as cal
import json
from amadeus import Client, ResponseError

# JSON 파일에서 API 키와 시크릿 불러오기
with open('API_key.json', 'r') as file:
    API_key = json.load(file)

API_KEY = API_key['AMADEUS_API_KEY']
API_SECRET = API_key['AMADEUS_API_SECRET']

amadeus = Client(client_id=API_KEY, client_secret=API_SECRET)

def fetch_german_airports_from_icn():
    try:
        # 인천국제공항에서 출발하는 항공편 검색
        response = amadeus.shopping.flight_destinations.get(origin='ICN')
        # 독일로 가는 항공편이 있는 공항만 필터링
        german_airports = set()
        for flight in response.data:
            if flight['destination'][:2] == 'DE':  # 독일 공항 코드는 'DE'로 시작
                german_airports.add(flight['destination'])
        return list(german_airports)
    except ResponseError as error:
        print(f"Amadeus API Error: {error}")
        return []

def fetch_flight_info(origin, destination, departure_date, return_date):
    try:
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=origin,
            destinationLocationCode=destination,
            departureDate=departure_date,
            returnDate=return_date,
            adults=1)
        return response.data
    except ResponseError as error:
        print(error)
        return []

class JapanTravelHelperApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Travel Planning Helper')
        self.geometry('600x500')
        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        self.initialize_origin_selector()
        self.initialize_destination_selector()
        self.initialize_date_selectors()
        self.initialize_search_quit_buttons()

    def initialize_origin_selector(self):
        origin_label = ttk.Label(self, text='Departure Airport (Incheon International Airport):', font=('Helvetica', 10))
        origin_label.pack(pady=10)

        self.origin_var = tk.StringVar(value='ICN')  # 인천국제공항 고정
        origin_combobox = ttk.Combobox(self, textvariable=self.origin_var, values=['ICN'], state='readonly', width=47)
        origin_combobox.pack(pady=10)

    def initialize_destination_selector(self):
        destination_label = ttk.Label(self, text='Choose your destination in Germany:', font=('Helvetica', 10))
        destination_label.pack(pady=10)

        self.destination_var = tk.StringVar()
        self.destination_combobox = ttk.Combobox(self, textvariable=self.destination_var, width=47)
        self.destination_combobox.pack(pady=10)
        self.populate_destination_combobox()

    def populate_destination_combobox(self):
        german_airports = fetch_german_airports_from_icn()
        if german_airports:
            self.destination_combobox['values'] = german_airports
        else:
            messagebox.showerror("Error", "No German airports found from ICN.")

    def initialize_date_selectors(self):
        date_frame = ttk.Frame(self)
        date_frame.pack(pady=20)

        departure_date_label = ttk.Label(date_frame, text='Choose your departure date:', font=('Helvetica', 10))
        departure_date_label.grid(row=0, column=0, padx=10, pady=10)
        self.departure_date_calendar = cal.Calendar(date_frame, selectmode='day')
        self.departure_date_calendar.grid(row=1, column=0, padx=10)
    
        return_date_label = ttk.Label(date_frame, text='Choose your return date:', font=('Helvetica', 10))
        return_date_label.grid(row=0, column=1, padx=10, pady=10)
        self.return_date_calendar = cal.Calendar(date_frame, selectmode='day')
        self.return_date_calendar.grid(row=1, column=1, padx=10)

    def initialize_search_quit_buttons(self):
        search_button = ttk.Button(self, text='Search', command=self.on_search)
        search_button.pack(pady=10)

        quit_button = ttk.Button(self, text='Quit', command=self.destroy)
        quit_button.pack(side='right', padx=10, pady=10)

    def on_search(self, event=None):
        origin = self.origin_var.get()
        destination = self.destination_var.get()
        departure_date = self.departure_date_calendar.get_date()
        return_date = self.return_date_calendar.get_date()

        if origin and destination and departure_date and return_date:
            flights = fetch_flight_info(origin, destination, departure_date, return_date)
            self.display_flights(flights)
        else:
            messagebox.showerror("Error", "Please enter all fields correctly.")

    def display_flights(self, flights):
        result_window = tk.Toplevel(self)
        result_window.title('Flight Results')

        for flight in flights:
            flight_info = f"Departure: {flight['itineraries'][0]['segments'][0]['departure']['iataCode']} on {flight['itineraries'][0]['segments'][0]['departure']['at']}\n"
            flight_info += f"Arrival: {flight['itineraries'][0]['segments'][-1]['arrival']['iataCode']} on {flight['itineraries'][0]['segments'][-1]['arrival']['at']}\n"
            flight_info += f"Price: {flight['price']['total']} {flight['price']['currency']}\n"

            label = ttk.Label(result_window, text=flight_info, font=('Helvetica', 10))
            label.pack()

        if not flights:
            label = ttk.Label(result_window, text="No flights found.", font=('Helvetica', 10))
            label.pack()

def main():
    app = JapanTravelHelperApp()
    app.mainloop()

if __name__ == "__main__":
    main()
