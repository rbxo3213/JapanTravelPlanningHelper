import tkinter as tk
from amadeus import Client, ResponseError
import json

# Load API keys from the JSON file
with open('API_key.json', 'r') as file:
    api_keys = json.load(file)
    API_KEY = api_keys['AMADEUS_API_KEY']
    API_SECRET = api_keys['AMADEUS_API_SECRET']

# Initialize Amadeus client
amadeus = Client(client_id=API_KEY, client_secret=API_SECRET)

def get_city_iata_code(city_name):
    try:
        response = amadeus.reference_data.locations.cities.get(keyword=city_name)
        cities = response.data
        if cities:
            return cities[0]['iataCode']
    except ResponseError as error:
        return "Error: " + str(error)

def fetch_iata_code():
    city_name = city_entry.get()
    iata_code = get_city_iata_code(city_name)
    iata_label.config(text="IATA Code: " + str(iata_code))

# Set up the Tkinter window
window = tk.Tk()
window.title("IATA Code Fetcher")

# Create entry widget for city name
city_entry = tk.Entry(window)
city_entry.pack()

# Button to fetch IATA code
fetch_button = tk.Button(window, text="Get IATA Code", command=fetch_iata_code)
fetch_button.pack()

# Label to display the result
iata_label = tk.Label(window, text="IATA Code: ")
iata_label.pack()

# Run the application
window.mainloop()
