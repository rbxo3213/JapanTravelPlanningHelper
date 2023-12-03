import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
from datetime import datetime
import geopy.distance

class GuiApplication:
    def __init__(self, root, flight_search, hotel_search):
        self.root = root
        self.flight_search = flight_search
        self.hotel_search = hotel_search
        self.setup_ui()

    def setup_ui(self):
        self.origin_var = tk.StringVar(value='Seoul(ICN)')
        self.destination_var = tk.StringVar(value='Tokyo(HND)')

        # UI 구성 요소 정의
        tk.Label(self.root, text="Origin:").grid(row=0, column=0, sticky='e')
        origin_combobox = ttk.Combobox(self.root, textvariable=self.origin_var, values=list(self.flight_search.airports_korea.values()))
        origin_combobox.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.root, text="Destination:").grid(row=1, column=0, sticky='e')
        destination_combobox = ttk.Combobox(self.root, textvariable=self.destination_var, values=list(self.flight_search.airports_japan.values()))
        destination_combobox.grid(row=1, column=1, padx=5, pady=5)

        self.departure_calendar = Calendar(self.root, selectmode='day')
        self.departure_calendar.grid(row=2, column=1, padx=5, pady=5)
        tk.Label(self.root, text="Departure Date:").grid(row=2, column=0, sticky='e')

        self.return_calendar = Calendar(self.root, selectmode='day')
        self.return_calendar.grid(row=3, column=1, padx=5, pady=5)
        tk.Label(self.root, text="Return Date:").grid(row=3, column=0, sticky='e')

        search_flight_button = tk.Button(self.root, text="Search Flights", command=self.trigger_flight_search)
        search_flight_button.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

        search_hotel_button = tk.Button(self.root, text="Search Hotels", command=self.trigger_hotel_search)
        search_hotel_button.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

    def trigger_flight_search(self):
        departure_date = self.departure_calendar.get_date()
        return_date = self.return_calendar.get_date()
        self.flight_search.search_flights(self.origin_var.get(), self.destination_var.get(), departure_date, return_date)

    def trigger_hotel_search(self):
        selected_district = self.destination_var.get()  # 예시로 목적지 변수 사용
        self.hotel_search.search_and_book_hotel(selected_district)
