# flight_search.py
from BaseApplication import BaseApplication
from tkinter import ttk, messagebox
import tkinter as tk

class FlightSearch(BaseApplication):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app

    def search_flights(self, origin_code, destination_code, departure_date, return_date):
        try:
            response = self.amadeus.shopping.flight_offers_search.get(
                originLocationCode=origin_code,
                destinationLocationCode=destination_code,
                departureDate=departure_date,
                returnDate=return_date,
                adults=1
            )
            return response.data
        except Exception as error:
            messagebox.showerror("Error", f"An error occurred: {error}")
            return None

    @staticmethod
    def display_flight_details(root, flight_data):
        new_window = tk.Toplevel(root)
        new_window.title("항공편 세부 정보")
        new_window.geometry("900x600")  # 창 크기 조정

        # Scrollable canvas and frame
        canvas = tk.Canvas(new_window)
        scrollbar = ttk.Scrollbar(new_window, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        # Configure canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        # 스크롤바와 캔버스를 바인딩
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        # Display each flight offer
        for offer in flight_data:
            # Create a frame for each round trip
            round_trip_frame = ttk.Frame(scrollable_frame, padding=10)
            round_trip_frame.pack(fill='x', expand=True, pady=10)
            round_trip_frame.configure(borderwidth=2, relief="groove")

            # Create labels for each leg of the trip
            for i, itinerary in enumerate(offer['itineraries']):
                flight_info = f"항공편 {i+1} - 출발: {itinerary['segments'][0]['departure']['iataCode']} {itinerary['segments'][0]['departure']['at']}, " \
                              f"도착: {itinerary['segments'][-1]['arrival']['iataCode']} {itinerary['segments'][-1]['arrival']['at']}, " \
                              f"소요 시간: {BaseApplication.convert_duration(itinerary['duration'])}, " \
                              f"항공사: {itinerary['segments'][0]['carrierCode']}"
                label = tk.Label(round_trip_frame, text=flight_info, bg="#f0f0f0", fg="black", font=('Gothic', 12))
                label.pack(fill='x', expand=True, pady=5)

            # Display price in KRW
            price_info = f"가격: {BaseApplication.convert_price(offer['price']['total'])}원"
            price_label = tk.Label(round_trip_frame, text=price_info, bg="#d0e0d0", fg="black", font=('Gothic', 14, 'bold'))
            price_label.pack(fill='x', expand=True, pady=5)

        # Pack everything
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")