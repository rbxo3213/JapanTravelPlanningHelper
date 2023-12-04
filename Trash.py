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

with open('transport_info.json', 'r') as file:
    transport_data = json.load(file)

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

def display_flight_details(flight_data, flight_frame):
    for widget in flight_frame.winfo_children():
        widget.destroy()
    
    for offer in flight_data:
        round_trip_frame = ttk.Frame(flight_frame, padding=10, borderwidth=2, relief="groove")
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

    flight_frame.update_idletasks()

# 이 함수를 호출할 때는 'flights' 카테고리에 해당하는 scrollable_frame을 전달합니다.
# 예: display_flight_details(response_data, scrollable_frames['flights'])


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
        display_flight_details(response.data, scrollable_frames['flights'])
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
        display_hotels(hotels, scrollable_frames['hotels'])
    except ResponseError as error:
        messagebox.showerror("Error", "Failed to fetch hotels: " + str(error))

def display_hotels(hotels, hotel_frame):
    # Clear the frame
    for widget in hotel_frame.winfo_children():
        widget.destroy()

    for hotel in hotels:
        # 호텔 가격을 엔화에서 원화로 변환합니다.
        price_krw = convert_price_from_jpy_to_krw(hotel['offers'][0]['price']['total'])

        hotel_frame_individual = ttk.Frame(hotel_frame, padding=10, borderwidth=2, relief="groove")
        hotel_frame_individual.pack(fill='x', expand=True, pady=5)
        
        hotel_name_label = ttk.Label(hotel_frame_individual, text=hotel['hotel']['name'], font=('Gothic', 12, 'bold'))
        hotel_name_label.pack(side='left', fill='x', expand=True)
        
        hotel_price_label = ttk.Label(hotel_frame_individual, text=f"Price: {price_krw} KRW", font=('Gothic', 12))
        hotel_price_label.pack(side='left', fill='x', expand=True)

    hotel_frame.update_idletasks()


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
                display_pois(response.data, scrollable_frames['pois'])
                break
            except ResponseError as error:
                error_code = error.response.status_code
                error_description = error.response.result
                #messagebox.showerror(
                #    "Error",
                #    f"Failed to fetch POIs for {region_name}: {error_code} - {error_description}"
                #) amadeus api test key에서 일본 지역은 사용할 수 없다고 해서 주석처리 함.

def display_pois(pois_data, poi_frame):
    for widget in poi_frame.winfo_children():
        widget.destroy()

    for poi in pois_data:
        poi_frame_individual = ttk.Frame(poi_frame, padding=10)
        poi_frame_individual.pack(fill='x', expand=True)

        poi_name_label = ttk.Label(poi_frame_individual, text=poi['name'], font=('Gothic', 12, 'bold'))
        poi_name_label.pack(side='left', fill='x', expand=True)

        poi_category_label = ttk.Label(poi_frame_individual, text=f"Category: {poi['category']}", font=('Gothic', 12))
        poi_category_label.pack(side='left', fill='x', expand=True)

    poi_frame.update_idletasks()

def display_transport_info(destination_code, transport_frame):
    destination_city = destination_var.get()
    destination_code = convert_iata_code(next((code for code, city in airports_japan.items() if city == destination_city), None))
    iata_code = convert_iata_code(destination_code)
    
    # Fetch the transport information for the IATA code
    transport_info = transport_data.get(iata_code)
    
    if transport_info:
        # Display transport information in a new window
        display_transport_details(transport_info, scrollable_frames['transport'])
    else:
        messagebox.showwarning("Not Found", "No transport information found for the selected destination.")

def display_transport_details(transport_info, transport_frame):
    for widget in transport_frame.winfo_children():
        widget.destroy()

    # Displaying transport details in the given frame
    pass_names = transport_info['PassName']
    for idx, name in enumerate(pass_names):
        btn = ttk.Button(transport_frame, text=name, command=lambda n=name: messagebox.showinfo("Selection", f"Selected PassName: {n}"))
        btn.pack(side='top', fill='x', expand=True, padx=5, pady=5)

    coverage_label = ttk.Label(transport_frame, text=transport_info['Coverage'], font=('Gothic', 12))
    coverage_label.pack(side='top', fill='x', expand=True)

    for duration in transport_info['DurationOptions']:
        btn = ttk.Button(transport_frame, text=duration, command=lambda d=duration: messagebox.showinfo("Selection", f"Selected Duration Option: {d}"))
        btn.pack(side='top', fill='x', expand=True, padx=5, pady=5)

    notes_label = ttk.Label(transport_frame, text=transport_info['Notes'], font=('Gothic', 12))
    notes_label.pack(side='top', fill='x', expand=True)

    transport_frame.update_idletasks()


# Initialize the main GUI window
root = tk.Tk()
root.title("JTPH (Japan Travle Planning Helper)")

# Define variables for the GUI 사용자 인터페이스 설정


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

search_button = tk.Button(root, text="Search", command=lambda: [search_flights(), fetch_hotel_list(), fetch_pois(), display_transport_info(destination_var.get(), scrollable_frames['transport'])])
search_button.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

search_button = tk.Button(root, text="Search", command=lambda: [search_flights(), fetch_hotel_list(), fetch_pois(), display_transport_info(destination_var.get(), scrollable_frames['transport'])])

search_button.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

main_frame = ttk.Frame(root)
main_frame.grid(row=6, column=0, columnspan=2, sticky='nsew')

# 메인 프레임의 각 행과 열에 대한 구성
for i in range(4):
    main_frame.grid_rowconfigure(i, weight=1)
    main_frame.grid_columnconfigure(0, weight=1)

# 프레임과 캔버스를 보관할 딕셔너리를 만듭니다.
frames = {}
canvases = {}
scrollbars = {}
scrollable_frames = {}

# 각 카테고리에 대해 네 개의 프레임, 캔버스, 스크롤바를 생성합니다.
for i, category in enumerate(["flights", "hotels", "pois", "transport"]):
    frame = ttk.Frame(main_frame, width=850, height=250)  # Set the size
    frame.grid(row=i, column=1, sticky='nsew', padx=2, pady=2)  # Place in a 4x1 grid
    frames[category] = frame

    canvases[category] = tk.Canvas(frames[category])
    scrollbars[category] = ttk.Scrollbar(frames[category], orient='vertical', command=canvases[category].yview)
    scrollbars[category].grid(row=0, column=1, sticky='ns')

    canvases[category].configure(yscrollcommand=scrollbars[category].set)
    canvases[category].grid(row=0, column=0, sticky='nsew')

    scrollable_frames[category] = ttk.Frame(canvases[category])
    canvases[category].create_window((0, 0), window=scrollable_frames[category], anchor='nw')

    canvases[category].bind('<Configure>', lambda e, c=canvases[category]: c.configure(scrollregion=c.bbox("all")))

def on_configure(event, canvas):
    canvas.configure(scrollregion=canvas.bbox('all'))

for category, canvas in canvases.items():
    canvas.bind('<Configure>', lambda event, canvas=canvas: on_configure(event, canvas))
    scrollable_frames[category].bind("<Configure>", lambda event, canvas=canvas: on_configure(event, canvas))
    root.bind("<MouseWheel>", lambda event, canvas=canvas: on_mousewheel(event, canvas))

# 수정된 부분: main_frame의 각 행과 열에 대한 구성
main_frame.grid(row=6, column=0, columnspan=2, sticky='nsew')
# 4x1 행렬로 변경하기 위해 row의 범위를 조정
for i in range(4):
    main_frame.grid_rowconfigure(i, weight=1)
    # columnspan을 2에서 1로 변경
    main_frame.grid_columnconfigure(0, weight=1, uniform='fred')

frames[category].grid(row=i, column=0, sticky='nsew', padx=2, pady=2)

root.update_idletasks()
# root의 크기를 조정하고 메인 루프를 시작합니다
root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}")
root.mainloop()
