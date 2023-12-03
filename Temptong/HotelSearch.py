# hotel_search.py
from BaseApplication import BaseApplication
from tkinter import messagebox
import tkinter as tk
import geopy.distance

class HotelSearch(BaseApplication):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app

    def search_hotels(self, city_code, selected_district, district_coords):
        try:
            response = self.amadeus.reference_data.locations.hotels.by_city.get(cityCode=city_code)
            hotels_data = response.data
            return self.sort_hotels(hotels_data, district_coords)
        except Exception as error:
            messagebox.showerror("Error", f"An error occurred: {error}")
            return None

    @staticmethod
    def sort_hotels(hotels_data, district_coords):
        return sorted(
            hotels_data,
            key=lambda hotel: geopy.distance.distance(
                (hotel['geoCode']['latitude'], hotel['geoCode']['longitude']),
                district_coords
            ).km
        )

    @staticmethod
    def display_hotels(root, hotels_data, selected_district):
        hotels_window = tk.Toplevel(root)
        hotels_window.title("Available Hotels")
        hotels_window.geometry("900x600")

        scrollbar = ttk.Scrollbar(hotels_window)
        scrollbar.pack(side='right', fill='y')

        hotels_listbox = tk.Listbox(hotels_window, yscrollcommand=scrollbar.set)
        for hotel in hotels_data:
            try:
                hotel_name = hotel.get('name', 'No Name')
                hotel_address = ', '.join(hotel.get('address', {}).get('lines', ['No Address']))
                hotels_listbox.insert(tk.END, f"{hotel_name} - {hotel_address}")
            except Exception as e:
                print(f"Error parsing hotel data: {e}")
                hotels_listbox.insert(tk.END, "Error retrieving hotel information")

        hotels_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=hotels_listbox.yview)