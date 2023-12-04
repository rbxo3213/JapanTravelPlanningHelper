
import tkinter as tk
from amadeus import Client
import json
from MainApplication import MainApplication
from FlightSearch import FlightSearch
from HotelSearch import HotelSearch

# Load API keys from the JSON file
with open('API_key.json', 'r') as file:
    api_keys = json.load(file)
    API_KEY = api_keys['AMADEUS_API_KEY']
    API_SECRET = api_keys['AMADEUS_API_SECRET']

# Load airport data and regions data from JSON files
with open('airports.json', 'r') as file:
    airports_data = json.load(file)
    airports_korea = airports_data['Korea']
    airports_japan = airports_data['Japan']

with open('regions.json', 'r') as file:
    regions_data = json.load(file)
    regions = regions_data

# Initialize Amadeus client
amadeus = Client(client_id=API_KEY, client_secret=API_SECRET)

amadeus_client = Client(client_id=API_KEY, client_secret=API_SECRET)
root = tk.Tk()
# Initialize FlightSearch and HotelSearch
flight_search = FlightSearch(amadeus_client, airports_korea, airports_japan)
hotel_search = HotelSearch(amadeus_client, airports_japan, regions)
app = MainApplication(root, flight_search, hotel_search, airports_data['Korea'], airports_data['Japan'], regions)
root.mainloop()
