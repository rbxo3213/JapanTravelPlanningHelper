import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
from amadeus import Client, ResponseError
from datetime import datetime
import json
import os
import math
import geopy.distance
import geocoder

# Load API keys from the JSON file
with open('API_key.json', 'r') as file:
    api_keys = json.load(file)
    API_KEY = api_keys['AMADEUS_API_KEY']
    API_SECRET = api_keys['AMADEUS_API_SECRET']

# Initialize Amadeus client
amadeus = Client(client_id=API_KEY, client_secret=API_SECRET)


class Hotel:
    def __init__(self, hotel_data):
        self.hotel_data = hotel_data

    def construct_hotel(self):
        offer = {}
        try:
            if 'offers' in self.hotel_data and self.hotel_data['offers']:
                offer['price'] = self.hotel_data['offers'][0]['price']['total']
            if 'hotel' in self.hotel_data:
                offer['name'] = self.hotel_data['hotel'].get('name', 'No Name')
                offer['hotelID'] = self.hotel_data['hotel'].get('hotelId', 'No ID')
                lat = self.hotel_data['hotel'].get('latitude')
                lon = self.hotel_data['hotel'].get('longitude')
                if lat and lon:
                    address = geocoder.osm([lat, lon], method='reverse')
                    offer['address'] = self.construct_address(address.json)
        except Exception as e:
            print(f"Error constructing hotel info: {e}")
        return offer

    @staticmethod
    def construct_address(address_json):
        street = address_json.get('street', 'Unknown Street')
        house_number = address_json.get('houseNumber') or address_json.get('housenumber', '')
        return f"{street} {house_number}".strip()


# Function to convert specific IATA codes to 'TYO'
def convert_iata_code(iata_code):
    if iata_code in ['HND', 'NRT']:
        return 'TYO'
    return iata_code

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
def show_hotels_by_district(district, check_in_date, check_out_date):
    # 지역에 따른 좌표 설정
    district_coords = {
        'Shibuya': (35.6620, 139.7036),
        'Shinjuku': (35.6938, 139.7036),
        'Ginza': (35.6721, 139.7708),
    }
    selected_coords = district_coords[district]

    # API 호출 및 호텔 정보 표시
    search_and_display_hotels(selected_coords, check_in_date, check_out_date)

    try:
        # Assuming you have check-in and check-out dates, 
        # otherwise you'll need to get them from the user's input
        check_in_date = '2023-01-01'  # Placeholder, use actual date
        check_out_date = '2023-01-03'  # Placeholder, use actual date

        # This should be a hotel search API call, which includes price data
        response = amadeus.shopping.hotel_offers_search.get(
            latitude=selected_coords[0],
            longitude=selected_coords[1],
            checkInDate=check_in_date,
            checkOutDate=check_out_date
        )
        hotels_data = response.data

        # Create Hotel instances and construct hotel offers
        hotel_offers = [Hotel(hotel).construct_hotel() for hotel in hotels_data]

        # Display hotels with their complete data
        display_hotels(hotel_offers)

    except ResponseError as error:
        messagebox.showerror("Error", f"An error occurred: {error}")


# Function to convert price from EUR to KRW
def convert_price(price):
    # Dummy conversion rate, you should use real-time rates or another method
    conversion_rate = 1350
    return int(float(price) * conversion_rate)


# Function to convert flight duration from ISO format (PT2H25M) to human-readable format (2h 25m)
def convert_duration(duration):
    try:
        hours = int(duration[2:duration.find('H')])
        minutes = int(duration[duration.find('H')+1:duration.find('M')])
        return f"{hours}h {minutes}m"
    except ValueError:
        return duration  # Return original if conversion is not possible

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

# 호텔 검색을 수행하고 결과를 표시하는 함수
def search_and_display_hotels(city_code, check_in_date, check_out_date):
    try:
        # 호텔 검색 API 호출
        response = amadeus.shopping.hotel_offers_search.get(
            cityCode=city_code, 
            checkInDate=check_in_date, 
            checkOutDate=check_out_date
        )
        hotels_data = response.data

        # 응답으로부터 호텔 정보 생성
        hotel_offers = [Hotel(hotel).construct_hotel() for hotel in hotels_data]

        # 호텔 정보 표시
        display_hotels(hotel_offers)

    except ResponseError as error:
        messagebox.showerror("Error", f"An error occurred: {error}")

# 사용자 입력으로부터 체크인, 체크아웃 날짜 얻기
# 날짜 형식을 '%Y-%m-%d'로 변환합니다.
def format_date(date_str):
    # 날짜 문자열을 공백으로 분할합니다.
    parts = date_str.split('.')
    # 공백을 제거하고, 각 부분을 정수로 변환합니다.
    parts = [int(part.strip()) for part in parts if part.strip()]
    # 세기를 더하여 연도를 완성합니다. (예: 23 -> 2023)
    parts[0] += 2000
    # 날짜 객체를 반환합니다.
    return datetime(parts[0], parts[1], parts[2]).date()

def search_and_book_hotel():
    selected_destination = destination_var.get()

    # IATA 코드 추출
    iata_code = selected_destination.split('(')[-1].rstrip(')')
    converted_iata_code = convert_iata_code(iata_code)

    # 캘린더 위젯으로부터 날짜를 가져와서 올바른 형식으로 변환합니다.
    check_in_date = format_date(departure_calendar.get_date())
    check_out_date = format_date(return_calendar.get_date())

    # 도쿄가 선택되었을 때만 지역 선택 창을 표시합니다.
    if converted_iata_code == 'TYO':
        district_window = tk.Toplevel(root)
        district_window.title("Select an Area")

        # 각 지역 버튼에 대한 콜백 설정
        for district in ['Shibuya', 'Shinjuku', 'Ginza']:
            btn = tk.Button(
                district_window,
                text=district,
                command=lambda d=district: show_hotels_by_district(d, check_in_date, check_out_date)
            )
            btn.pack()
    else:
        # 호텔 검색 및 표시 함수 호출
        search_and_display_hotels(converted_iata_code, check_in_date, check_out_date)

def display_hotels(hotel_offers):
    hotels_window = tk.Toplevel(root)
    hotels_window.title("Available Hotels")
    hotels_window.geometry("900x600")

    scrollbar = ttk.Scrollbar(hotels_window)
    scrollbar.pack(side='right', fill='y')

    hotels_listbox = tk.Listbox(hotels_window, yscrollcommand=scrollbar.set)
    for offer in hotel_offers:
        # Ensure all keys are present before accessing them
        name = offer.get('name', 'Unknown Hotel')
        address = offer.get('address', 'Unknown Address')
        price = offer.get('price', 'Unknown Price')
        hotel_info = f"{name} - {address}, Price: {price}"
        hotels_listbox.insert(tk.END, hotel_info)

    hotels_listbox.pack(side='left', fill='both', expand=True)
    scrollbar.config(command=hotels_listbox.yview)


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

# 호텔 검색 버튼 추가
hotel_search_button = tk.Button(root, text="Search Hotels", command=search_and_book_hotel)
hotel_search_button.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

# Start the main loop
root.mainloop()
