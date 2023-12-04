
import tkinter as tk
from tkinter import ttk, messagebox
from amadeus import ResponseError
from Utils import Utils

class FlightSearch:
    def __init__(self, amadeus_client, airports_korea, airports_japan):
        self.amadeus = amadeus_client
        self.airports_korea = airports_korea
        self.airports_japan = airports_japan

    def search_flights(self, origin_city, destination_city, departure_date, return_date, adults):
        origin_code = next((code for code, city in self.airports_korea.items() if city == origin_city), None)
        destination_code = next((code for code, city in self.airports_japan.items() if city == destination_city), None)

        try:
            response = self.amadeus.shopping.flight_offers_search.get(
                originLocationCode=origin_code,
                destinationLocationCode=destination_code,
                departureDate=departure_date,
                returnDate=return_date,
                adults=adults
            )
            self.display_flight_details(response.data)
        except ResponseError as error:
            messagebox.showerror("Error", f"An error occurred: {error}")

    def display_flight_details(self, flight_data):
        new_window = tk.Toplevel()
        new_window.title("Flight Details")
        new_window.geometry("860x300")

        canvas = tk.Canvas(new_window)
        scrollbar = ttk.Scrollbar(new_window, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        scrollbar.pack(side="right", fill="y")
        new_window.bind("<MouseWheel>", lambda e: Utils.on_mousewheel(e, canvas))

        for offer in flight_data:
            round_trip_frame = ttk.Frame(scrollable_frame, padding=10, borderwidth=2, relief="groove")
            round_trip_frame.pack(fill='x', expand=True, pady=10)
            for i, itinerary in enumerate(offer['itineraries']):
                flight_info = "Flight {} - Departure: {} {}, Arrival: {} {}, Duration: {}, Airline: {}".format(
                    i + 1,
                    itinerary['segments'][0]['departure']['iataCode'],
                    itinerary['segments'][0]['departure']['at'],
                    itinerary['segments'][-1]['arrival']['iataCode'],
                    itinerary['segments'][-1]['arrival']['at'],
                    Utils.convert_duration(itinerary['duration']),
                    itinerary['segments'][0]['carrierCode']
                )
                label = tk.Label(round_trip_frame, text=flight_info, bg="#f0f0f0", fg="black", font=('Gothic', 12))
                label.pack(fill='x', expand=True, pady=5)

            price_info = "Price: {} KRW".format(Utils.convert_price(offer['price']['total']))
            price_label = tk.Label(round_trip_frame, text=price_info, bg="#d0e0d0", fg="black", font=('Gothic', 14, 'bold'))
            price_label.pack(fill='x', expand=True, pady=5)

        canvas.pack(side="left", fill="both", expand=True)
