import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
from amadeus import Client, ResponseError
from datetime import datetime
import json
import os

# Load API keys from the JSON file
with open('API_key.json', 'r') as file:
    api_keys = json.load(file)
    API_KEY = api_keys['AMADEUS_API_KEY']
    API_SECRET = api_keys['AMADEUS_API_SECRET']

# Initialize Amadeus client
amadeus = Client(client_id=API_KEY, client_secret=API_SECRET)

# Separate the airports by country
airports_korea = {
    'ICN': 'Seoul(ICN)', 'GMP': 'Seoul(GMP)', 'PUS': 'Busan', 'CJU': 'Jeju',
    'MWX': 'Muan', 'YNY': 'Yangyang', 'CJJ': 'Cheongju', 'TAE': 'Daegu'
}
airports_japan = {
    'HND': 'Tokyo(HND)', 'NRT': 'Tokyo(NRT)', 'KIX': 'Osaka', 'FUK': 'Fukuoka',
    'NGO': 'Nagoya', 'HIJ': 'Hiroshima', 'HSG': 'Saga', 'FSZ': 'Shizuoka',
    'CTS': 'Sapporo', 'KKJ': 'Kitakyushu', 'TAK': 'Takamatsu',
    'KMJ': 'Kumamoto', 'MYJ': 'Matsuyama', 'OKA': 'Okinawa', 'SDJ': 'Sendai',
    'NGS': 'Nagasaki', 'TOY': 'Toyama'
}

# Function to convert flight duration from ISO format (PT2H25M) to human-readable format (2h 25m)
def convert_duration(duration):
    try:
        hours = int(duration[2:duration.find('H')])
        minutes = int(duration[duration.find('H')+1:duration.find('M')])
        return f"{hours}h {minutes}m"
    except ValueError:
        return duration  # Return original if conversion is not possible

# Function to convert price from EUR to KRW
def convert_price(price):
    # Dummy conversion rate, you should use real-time rates or another method
    conversion_rate = 1350
    return int(float(price) * conversion_rate)

# Function to convert specific IATA codes to 'TYO'
def convert_iata_code(iata_code):
    if iata_code in ['HND', 'NRT']:
        return 'TYO'
    return iata_code

# 항공편 세부 정보 창의 스크롤 기능 활성화
def display_flight_details(flight_data):
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
                          f"소요 시간: {convert_duration(itinerary['duration'])}, " \
                          f"항공사: {itinerary['segments'][0]['carrierCode']}"
            label = tk.Label(round_trip_frame, text=flight_info, bg="#f0f0f0", fg="black", font=('Gothic', 12))
            label.pack(fill='x', expand=True, pady=5)

        # Display price in KRW
        price_info = f"가격: {convert_price(offer['price']['total'])}원"
        price_label = tk.Label(round_trip_frame, text=price_info, bg="#d0e0d0", fg="black", font=('Gothic', 14, 'bold'))
        price_label.pack(fill='x', expand=True, pady=5)

    # Pack everything
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

# Function to search flights using Amadeus library
def search_flights():
    origin_city = origin_var.get()
    destination_city = destination_var.get()

    # 출발지와 목적지 공항 코드 찾기
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
            adults=1
        )
        display_flight_details(response.data)
    except ResponseError as error:
        messagebox.showerror("Error", f"An error occurred: {error}")

# Initialize the main GUI window
# Initialize the main GUI window
root = tk.Tk()
root.title("Search")

# Define variables for the GUI
origin_var = tk.StringVar(value='Seoul(ICN)')  # Default value
destination_var = tk.StringVar(value='Tokyo(HND)')  # Default value

# Create widgets for the GUI
tk.Label(root, text="Origin:").grid(row=0, column=0, sticky='e')
# 출발지 콤보박스에 한국 공항만 설정
origin_combobox = ttk.Combobox(root, textvariable=origin_var, values=list(airports_korea.values()))
origin_combobox.grid(row=0, column=1, padx=5, pady=5)

tk.Label(root, text="Destination:").grid(row=1, column=0, sticky='e')
# 도착지 콤보박스에 일본 공항만 설정
destination_combobox = ttk.Combobox(root, textvariable=destination_var, values=list(airports_japan.values()))
destination_combobox.grid(row=1, column=1, padx=5, pady=5)


departure_calendar = Calendar(root, selectmode='day')
departure_calendar.grid(row=2, column=1, padx=5, pady=5)
tk.Label(root, text="Departure Date:").grid(row=2, column=0, sticky='e')

return_calendar = Calendar(root, selectmode='day')
return_calendar.grid(row=3, column=1, padx=5, pady=5)
tk.Label(root, text="Return Date:").grid(row=3, column=0, sticky='e')

search_button = tk.Button(root, text="Search Flights", command=search_flights)
search_button.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

# Start the GUI
root.mainloop()

## 7C, OZ등의 항공사 코드 별 이미지 파일을 불러와서 표시하기.
## 항공권 정보 창 gkdgrid 크기 맞추기(가로 두 배 늘리기).
## 출 도착 도시 선택을 공항 IATA코드에서 도시 이름으로 변경하기.