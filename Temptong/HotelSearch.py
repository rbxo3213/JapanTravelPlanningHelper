
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from Utils import Utils
from amadeus import ResponseError
import math

class HotelSearch:
    def __init__(self, amadeus_client, airports_japan, regions):
        self.amadeus = amadeus_client
        self.airports_japan = airports_japan
        self.regions = regions

    def fetch_hotel_list(self, destination_city, check_in_date, check_out_date, adults):
        destination_code = Utils.convert_iata_code(next((code for code, city in self.airports_japan.items() if city == destination_city), None))

        try:
            hotel_list_response = self.amadeus.reference_data.locations.hotels.by_city.get(cityCode=destination_code)
            hotel_ids = [hotel['hotelId'] for hotel in hotel_list_response.data]

            hotel_offers_response = self.amadeus.shopping.hotel_offers_search.get(
                hotelIds=hotel_ids,
                checkInDate=check_in_date,
                checkOutDate=check_out_date,
                adults=adults
            )
            return hotel_offers_response.data
        except ResponseError as error:
            messagebox.showerror("Error", "Failed to fetch hotels: " + str(error))
            return []

    def display_hotels(self, hotels, iata_code):
        new_window = tk.Toplevel(root)
        new_window.title("Hotels List")
        new_window.geometry("860x300")

        # Main frame for list of hotels
        hotels_frame = ttk.Frame(new_window)
        hotels_frame.pack(fill=tk.BOTH, expand=True)

        # Scrollable list for hotels
        hotels_canvas = tk.Canvas(hotels_frame)
        hotels_scrollbar = ttk.Scrollbar(hotels_frame, orient="vertical", command=hotels_canvas.yview)
        hotels_scrollable_frame = ttk.Frame(hotels_canvas)

        hotels_canvas.configure(yscrollcommand=hotels_scrollbar.set)
        hotels_canvas.bind('<Configure>', lambda e: hotels_canvas.configure(scrollregion=hotels_canvas.bbox("all")))
        hotels_canvas_window = hotels_canvas.create_window((0, 0), window=hotels_scrollable_frame, anchor="nw")

        for hotel in hotels:
            # 호텔 가격을 엔화에서 원화로 변환합니다.
            price_krw = Utils.convert_price_from_jpy_to_krw(hotel['offers'][0]['price']['total'])

            hotel_frame = ttk.Frame(hotels_scrollable_frame, padding=10, borderwidth=2, relief="groove")
            hotel_frame.pack(fill='x', expand=True, pady=5)

            hotel_name_label = ttk.Label(hotel_frame, text=hotel['hotel']['name'], font=('Gothic', 12, 'bold'))
            hotel_name_label.pack(side='left', fill='x', expand=True)

            hotel_price_label = ttk.Label(hotel_frame, text=f"Price: {price_krw} KRW", font=('Gothic', 12))
            hotel_price_label.pack(side='left', fill='x', expand=True)

        hotels_scrollbar.pack(side='right', fill='y')
        hotels_canvas.pack(side='left', fill='both', expand=True)

        # Region buttons frame
        region_buttons_frame = ttk.Frame(new_window)
        region_buttons_frame.pack(fill=tk.X, expand=False)

        if iata_code in regions:
            for region_name, coords in regions[iata_code].items():
                region_button = ttk.Button(region_buttons_frame, text=region_name, command=lambda rn=region_name: sort_hotels(hotels, rn, hotels_scrollable_frame, hotels_canvas, hotels_canvas_window))
                region_button.pack(side='left', padx=5, pady=5)

        # Bind the scroll event to the canvas
        new_window.bind("<MouseWheel>", lambda e: hotels_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

    def sort_hotels(self, hotels, region_name, hotels_scrollable_frame, hotels_canvas, hotels_canvas_window):
        destination_code = convert_iata_code(next((code for code, city in airports_japan.items() if city == destination_var.get()), None))
        region_coords = regions[destination_code][region_name]

        def haversine(lat1, lon1, lat2, lon2):
            R = 6371
            phi1 = math.radians(lat1)
            phi2 = math.radians(lat2)
            delta_phi = math.radians(lat2 - lat1)
            delta_lambda = math.radians(lon2 - lon1)
            a = math.sin(delta_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            return R * c

        def get_hotel_coords(hotel):
            if 'latitude' in hotel['hotel'] and 'longitude' in hotel['hotel']:
                return hotel['hotel']['latitude'], hotel['hotel']['longitude']
            else:
                return None, None

        sorted_hotels = []
        for hotel in hotels:
            lat, lon = get_hotel_coords(hotel)
            if lat is not None and lon is not None:
                hotel['distance'] = haversine(region_coords['lat'], region_coords['lon'], lat, lon)
                sorted_hotels.append(hotel)
        sorted_hotels.sort(key=lambda x: x['distance'])

        # Clear the current hotel frames
        for widget in hotels_scrollable_frame.winfo_children():
            widget.destroy()

        # Add sorted hotel frames back into the canvas with converted prices
        for hotel in sorted_hotels:
            price_krw = Utils.convert_price_from_jpy_to_krw(hotel['offers'][0]['price']['total'])

            hotel_frame = ttk.Frame(hotels_scrollable_frame, padding=10, borderwidth=2, relief="groove")
            hotel_frame.pack(fill='x', expand=True, pady=5)

            hotel_name_label = ttk.Label(hotel_frame, text=hotel['hotel']['name'], font=('Gothic', 12, 'bold'))
            hotel_name_label.pack(side='left', fill='x', expand=True)

            hotel_price_label = ttk.Label(hotel_frame, text=f"Price: {price_krw} KRW", font=('Gothic', 12))
            hotel_price_label.pack(side='left', fill='x', expand=True)

        # Update the scroll region of the canvas
        hotels_canvas.configure(scrollregion=hotels_canvas.bbox("all"))
