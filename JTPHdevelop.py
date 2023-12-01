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

# 도시명을 IATA 코드로 변환하는 함수
def get_city_iata_code(city_name):
    # 일본 공항 딕셔너리에서 도시명에 해당하는 IATA 코드를 찾습니다.
    for code, name in airports_japan.items():
        if city_name in name:
            return code  # IATA 코드를 반환합니다.
    return None  # 일치하는 도시명이 없는 경우 None을 반환합니다.

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

# 호텔 검색 기능
def search_and_book_hotel():
    destination_city = destination_var.get().split(' ')[0]  # "Tokyo(HND)"에서 "Tokyo" 추출
    departure_date = departure_calendar.get_date()
    return_date = return_calendar.get_date()

    try:
        # 호텔 검색 API 호출
        hotel_offers_response = amadeus.shopping.hotel_offers_search.get(
            cityCode=destination_city,
            checkInDate=departure_date,
            checkOutDate=return_date
        )

        if hotel_offers_response.status_code == 200:
            hotels_data = hotel_offers_response.data
            display_hotels(hotels_data)
        else:
            messagebox.showerror("Error", f"API call failed with status code {hotel_offers_response.status_code}")
    except ResponseError as error:
        messagebox.showerror("Error", f"An error occurred: {error}")

# 호텔 목록을 표시하는 새 창
def display_hotels(hotels_data):
    hotels_window = tk.Toplevel(root)
    hotels_window.title("Available Hotels")
    hotels_window.geometry("900x600")  # 새 창의 크기 설정

    # 숙소 데이터를 표시하는 스크롤 가능한 리스트
    hotels_listbox = tk.Listbox(hotels_window)
    for hotel in hotels_data:
        hotel_name = hotel.get("hotel", {}).get("name", "Unknown Hotel")
        hotel_price = hotel.get("offers", [{}])[0].get("price", {}).get("total", "0")
        hotels_listbox.insert(tk.END, f"{hotel_name} - Price: {hotel_price}")

    hotels_listbox.pack(side="left", fill="both", expand=True)

# Initialize the main GUI window
root = tk.Tk()
root.title("Search")

# amadeus 객체에서 사용 가능한 메소드 목록을 확인
# print(dir(amadeus.shopping))


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

# 호텔 검색 및 예약 버튼
search_and_book_button = tk.Button(root, text="Search and Book Hotel", command=search_and_book_hotel)
search_and_book_button.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

# Start the GUI
root.mainloop()