import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
from FlightSearch import FlightSearch
from HotelSearch import HotelSearch

class MainApplication:
    def __init__(self, root, flight_search, hotel_search, airports_korea, airports_japan, regions):
        self.root = root
        self.flight_search = flight_search
        self.hotel_search = hotel_search
        self.airports_korea = airports_korea
        self.airports_japan = airports_japan
        self.regions = regions
        self.setup_ui()

    def setup_ui(self):
        self.origin_var = tk.StringVar(value='Seoul(ICN)')
        self.destination_var = tk.StringVar(value='Tokyo(HND)')
        self.adults_var = tk.IntVar(value=1)
        self.departure_calendar = Calendar(self.root, selectmode='day')
        self.departure_calendar.grid(row=2, column=1, padx=5, pady=5)
        
        self.return_calendar = Calendar(self.root, selectmode='day')
        self.return_calendar.grid(row=3, column=1, padx=5, pady=5)
        
        self.adults_var = tk.IntVar(value=1)
        
        tk.Label(self.root, text="Origin:").grid(row=0, column=0, sticky='e')
        origin_combobox = ttk.Combobox(self.root, textvariable=self.origin_var, values=list(self.airports_korea.values()))
        origin_combobox.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.root, text="Destination:").grid(row=1, column=0, sticky='e')
        destination_combobox = ttk.Combobox(self.root, textvariable=self.destination_var, values=list(self.airports_japan.values()))
        destination_combobox.grid(row=1, column=1, padx=5, pady=5)

        departure_calendar = Calendar(self.root, selectmode='day')
        departure_calendar.grid(row=2, column=1, padx=5, pady=5)
        tk.Label(self.root, text="Departure Date:").grid(row=2, column=0, sticky='e')

        return_calendar = Calendar(self.root, selectmode='day')
        return_calendar.grid(row=3, column=1, padx=5, pady=5)
        tk.Label(self.root, text="Return Date:").grid(row=3, column=0, sticky='e')

        tk.Label(self.root, text="Number of Adults:").grid(row=4, column=0, sticky='e')
        adults_spinbox = ttk.Spinbox(self.root, from_=1, to=10, textvariable=self.adults_var)
        adults_spinbox.grid(row=4, column=1, padx=5, pady=5)

        search_button = tk.Button(self.root, text="Search Flights and Hotels", command=self.search_flights_and_hotels)
        search_button.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

    def search_flights_and_hotels(self):
        # Retrieve selected dates and number of adults from the UI
        departure_date = self.departure_calendar.get_date()
        return_date = self.return_calendar.get_date()
        adults = self.adults_var.get()

        # Call the search_flights method with all required arguments
        self.flight_search.search_flights(
            self.origin_var.get(),
            self.destination_var.get(),
            departure_date,
            return_date,
            adults
        )
        self.hotel_search.fetch_hotel_list(self.destination_var.get(), ...)
        # Note: 필요한 파라미터를 전달하고, FlightSearch 및 HotelSearch의 메서드를 호출합니다.
