import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar, DateEntry
from amadeus import Client, ResponseError
from datetime import datetime
import json
import math

# Load API keys from the JSON file
with open('API_key.json', 'r') as file:
    api_keys = json.load(file)
    API_KEY = api_keys['AMADEUS_API_KEY']
    API_SECRET = api_keys['AMADEUS_API_SECRET']

# Load API keys from the JSON file
with open('PRODUCT_key.json', 'r') as file:
    api_keys = json.load(file)
    PRODUCT_KEY = api_keys['PRODUCT_API_KEY']
    PRODUCT_SECRET = api_keys['PRODUCT_API_SECRET']

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
#product = Client(client_id=PRODUCT_KEY, client_secret=PRODUCT_SECRET)

# Convert specific IATA codes to 'TYO' or 'OSA'
def convert_iata_code(iata_code):
    if iata_code in ['HND', 'NRT']:
        return 'TYO'
    if iata_code in ['KIX', 'ITM']:
        return 'OSA'
    return iata_code

# Convert price from EUR to KRW
def convert_price(price):
    conversion_rate = 1350  # Example conversion rate
    return int(float(price) * conversion_rate)

JPY_TO_KRW_CONVERSION_RATE = 10  # This is an example rate, please use the current accurate rate

def convert_price_from_jpy_to_krw(price_jpy):
    return int(float(price_jpy) * JPY_TO_KRW_CONVERSION_RATE)

# Convert flight duration from ISO format to human-readable format
def convert_duration(duration):
    try:
        hours = int(duration[2:duration.find('H')])
        minutes = int(duration[duration.find('H')+1:duration.find('M')])
        return f"{hours}h {minutes}m"
    except ValueError:
        return duration

def on_mousewheel(event, canvas):
    canvas.yview_scroll(int(-1*(event.delta/120)), "units")

# Display flight details in a new window
def display_flight_details(flight_data):
    new_window = tk.Toplevel(root)
    new_window.title("Flight Details")
    new_window.geometry("860x300")

    canvas = tk.Canvas(new_window)
    scrollbar = ttk.Scrollbar(new_window, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    # Add the scrollbar to the canvas
    scrollbar.pack(side="right", fill="y")
    # Bind the mousewheel scrolling to the scrollbar
    new_window.bind("<MouseWheel>", lambda e: on_mousewheel(e, canvas))

    for offer in flight_data:
        round_trip_frame = ttk.Frame(scrollable_frame, padding=10, borderwidth=2, relief="groove")
        round_trip_frame.pack(fill='x', expand=True, pady=10)
        for i, itinerary in enumerate(offer['itineraries']):
            flight_info = f"Flight {i+1} - Departure: {itinerary['segments'][0]['departure']['iataCode']} {itinerary['segments'][0]['departure']['at']}, " \
                          f"Arrival: {itinerary['segments'][-1]['arrival']['iataCode']} {itinerary['segments'][-1]['arrival']['at']}, " \
                          f"Duration: {convert_duration(itinerary['duration'])}, " \
                          f"Airline: {itinerary['segments'][0]['carrierCode']}"
            label = tk.Label(round_trip_frame, text=flight_info, bg="#f0f0f0", fg="black", font=('Gothic', 12))
            label.pack(fill='x', expand=True, pady=5)

        price_info = f"Price: {convert_price(offer['price']['total'])} KRW"
        price_label = tk.Label(round_trip_frame, text=price_info, bg="#d0e0d0", fg="black", font=('Gothic', 14, 'bold'))
        price_label.pack(fill='x', expand=True, pady=5)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

# Search flights function
def search_flights():
    origin_city = origin_var.get()
    destination_city = destination_var.get()

    origin_code = next((code for code, city in airports_korea.items() if city == origin_city), None)
    destination_code = next((code for code, city in airports_japan.items() if city == destination_city), None)
    departure_date = datetime.strptime(departure_calendar.get_date(), '%y. %m. %d.').strftime('%Y-%m-%d')
    return_date = datetime.strptime(return_calendar.get_date(), '%y. %m. %d.').strftime('%Y-%m-%d')

    try:
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=origin_code,
            destinationLocationCode=destination_code,
            departureDate=departure_date,
            returnDate=return_date,
            adults=adults_var.get()
        )
        display_flight_details(response.data)
    except ResponseError as error:
        messagebox.showerror("Error", f"An error occurred: {error}")

# Fetch hotel list function
def fetch_hotel_list():
    destination_city = destination_var.get()
    destination_code = convert_iata_code(next((code for code, city in airports_japan.items() if city == destination_city), None))

    check_in_date = datetime.strptime(departure_calendar.get_date(), '%y. %m. %d.').strftime('%Y-%m-%d')
    check_out_date = datetime.strptime(return_calendar.get_date(), '%y. %m. %d.').strftime('%Y-%m-%d')

    try:
        hotel_list_response = amadeus.reference_data.locations.hotels.by_city.get(cityCode=destination_code)
        hotel_ids = [hotel['hotelId'] for hotel in hotel_list_response.data]

        hotel_offers_response = amadeus.shopping.hotel_offers_search.get(
            hotelIds=hotel_ids,
            checkInDate=check_in_date,
            checkOutDate=check_out_date,
            adults=adults_var.get()
        )
        hotels = hotel_offers_response.data
        display_hotels(hotels, destination_code)
    except ResponseError as error:
        messagebox.showerror("Error", "Failed to fetch hotels: " + str(error))

def display_hotels(hotels, iata_code):
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
        price_krw = convert_price_from_jpy_to_krw(hotel['offers'][0]['price']['total'])

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


# Sort hotels function
def sort_hotels(hotels, region_name, hotels_scrollable_frame, hotels_canvas, hotels_canvas_window):
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
        price_krw = convert_price_from_jpy_to_krw(hotel['offers'][0]['price']['total'])

        hotel_frame = ttk.Frame(hotels_scrollable_frame, padding=10, borderwidth=2, relief="groove")
        hotel_frame.pack(fill='x', expand=True, pady=5)
        
        hotel_name_label = ttk.Label(hotel_frame, text=hotel['hotel']['name'], font=('Gothic', 12, 'bold'))
        hotel_name_label.pack(side='left', fill='x', expand=True)
        
        hotel_price_label = ttk.Label(hotel_frame, text=f"Price: {price_krw} KRW", font=('Gothic', 12))
        hotel_price_label.pack(side='left', fill='x', expand=True)

    # Update the scroll region of the canvas
    hotels_canvas.configure(scrollregion=hotels_canvas.bbox("all"))

def fetch_pois():
    destination_iata_code = convert_iata_code(next((code for code, city in airports_japan.items() if city == destination_var.get()), None))

    with open('regions.json', 'r') as file:
        regions_data = json.load(file)

    if destination_iata_code in regions_data:
        region_coords = regions_data[destination_iata_code]

        for region_name, coords in region_coords.items():
            try:
                response = amadeus.reference_data.locations.points_of_interest.get(
                    latitude=41.397158,
                    longitude=2.160873,
                    radius=2
                )
                display_pois(response.data, region_name)
                break
            except ResponseError as error:
                error_code = error.response.status_code
                error_description = error.response.result
                #messagebox.showerror(
                #    "Error",
                #    f"Failed to fetch POIs for {region_name}: {error_code} - {error_description}"
                #) amadeus api test key에서 일본 지역은 사용할 수 없다고 해서 주석처리 함.



def display_pois(pois_data, region_name):
    new_window = tk.Toplevel(root)
    new_window.title(f"Points of Interest in {region_name}")
    new_window.geometry("860x600")

    pois_canvas = tk.Canvas(new_window)
    pois_scrollbar = ttk.Scrollbar(new_window, orient="vertical", command=pois_canvas.yview)
    pois_scrollable_frame = ttk.Frame(pois_canvas)

    pois_canvas.configure(yscrollcommand=pois_scrollbar.set)
    pois_canvas.bind('<Configure>', lambda e: pois_canvas.configure(scrollregion=pois_canvas.bbox("all")))
    pois_canvas.create_window((0, 0), window=pois_scrollable_frame, anchor="nw")

    pois_scrollbar.pack(side="right", fill="y")
    pois_canvas.pack(side="left", fill="both", expand=True)

    # Bind the mousewheel scrolling to the scrollbar
    new_window.bind("<MouseWheel>", lambda e: on_mousewheel(e, pois_canvas))

    for poi in pois_data:
        poi_frame = ttk.Frame(pois_scrollable_frame, padding=10)
        poi_frame.pack(fill='x', expand=True)

        poi_name_label = ttk.Label(poi_frame, text=poi['name'], font=('Gothic', 12, 'bold'))
        poi_name_label.pack(side='left', fill='x', expand=True)

        poi_category_label = ttk.Label(poi_frame, text=f"Category: {poi['category']}", font=('Gothic', 12))
        poi_category_label.pack(side='left', fill='x', expand=True)


# Initialize the main GUI window
root = tk.Tk()
root.title("Flight and Hotel Booking Application")

# Define variables for the GUI
origin_var = tk.StringVar(value='Seoul(ICN)')  # Default value
destination_var = tk.StringVar(value='Tokyo(HND)')  # Default value
adults_var = tk.IntVar(value=1)  # Default value

# Create widgets for the GUI
tk.Label(root, text="Origin:").grid(row=0, column=0, sticky='e')
origin_combobox = ttk.Combobox(root, textvariable=origin_var, values=list(airports_korea.values()))
origin_combobox.grid(row=0, column=1, padx=5, pady=5)

tk.Label(root, text="Destination:").grid(row=1, column=0, sticky='e')
destination_combobox = ttk.Combobox(root, textvariable=destination_var, values=list(airports_japan.values()))
destination_combobox.grid(row=1, column=1, padx=5, pady=5)

departure_calendar = Calendar(root, selectmode='day')
departure_calendar.grid(row=2, column=1, padx=5, pady=5)
tk.Label(root, text="Departure Date:").grid(row=2, column=0, sticky='e')

return_calendar = Calendar(root, selectmode='day')
return_calendar.grid(row=3, column=1, padx=5, pady=5)
tk.Label(root, text="Return Date:").grid(row=3, column=0, sticky='e')

tk.Label(root, text="Number of Adults:").grid(row=4, column=0, sticky='e')
adults_spinbox = ttk.Spinbox(root, from_=1, to=10, textvariable=adults_var)
adults_spinbox.grid(row=4, column=1, padx=5, pady=5)

search_button = tk.Button(root, text="Search Flights and Hotels", command=lambda: [search_flights(), fetch_hotel_list(), fetch_pois()])
search_button.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

# Start the main loop
root.mainloop()
