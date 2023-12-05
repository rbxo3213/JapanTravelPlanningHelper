import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from amadeus import Client, ResponseError
import json
import datetime
import math
# API 키 로드 및 Amadeus 클라이언트 초기화
with open('API_key.json', 'r') as file:
    api_keys = json.load(file)
    amadeus = Client(client_id=api_keys['AMADEUS_API_KEY'], client_secret=api_keys['AMADEUS_API_SECRET'])

# 일본 주요 지역 IATA 코드 목록
iata_codes = ["TYO", "OSA", "HND", "NRT", "KIX", "CTS", "FUK", "OKA", "ITM", "NGO"]

# Load regional data from a JSON file
with open('regions.json', 'r') as file:
    regions_data = json.load(file)
    regions = regions_data

# UI 초기화
window = tk.Tk()
window.title("Hotel Booking Application")

# UI 요소 생성
label_iata = ttk.Label(window, text="IATA Code")
label_adults = ttk.Label(window, text="Adults")
label_checkin = ttk.Label(window, text="Check-In Date")
label_checkout = ttk.Label(window, text="Check-Out Date")
combo_iata = ttk.Combobox(window, values=iata_codes)
spin_adults = ttk.Spinbox(window, from_=1, to=10)
date_checkin = DateEntry(window, date_pattern='y-mm-dd')
date_checkout = DateEntry(window, date_pattern='y-mm-dd')
button_search = ttk.Button(window, text="Search Hotels", command=lambda: fetch_hotel_list())

# UI 요소 배치
label_iata.grid(row=0, column=0, padx=5, pady=5)
combo_iata.grid(row=0, column=1, padx=5, pady=5)
label_adults.grid(row=1, column=0, padx=5, pady=5)
spin_adults.grid(row=1, column=1, padx=5, pady=5)
label_checkin.grid(row=2, column=0, padx=5, pady=5)
date_checkin.grid(row=2, column=1, padx=5, pady=5)
label_checkout.grid(row=3, column=0, padx=5, pady=5)
date_checkout.grid(row=3, column=1, padx=5, pady=5)
button_search.grid(row=4, columnspan=2, padx=5, pady=5)

# 호텔 리스트 가져오기 함수
def fetch_hotel_list():
    iata_code = combo_iata.get()
    adults = spin_adults.get()
    check_in_date = date_checkin.get_date().isoformat()
    check_out_date = date_checkout.get_date().isoformat()

    # HND, NRT를 TYO로 변환
    if iata_code in ["HND", "NRT"]:
        iata_code = "TYO"

    try:
        # 호텔 리스트 API 호출
        hotel_list_response = amadeus.reference_data.locations.hotels.by_city.get(cityCode=iata_code)
        hotel_ids = [hotel['hotelId'] for hotel in hotel_list_response.data]

        # 호텔 오퍼 API 호출
        hotel_offers_response = amadeus.shopping.hotel_offers_search.get(hotelIds=hotel_ids, checkInDate=check_in_date, checkOutDate=check_out_date, adults=adults)
        hotels = hotel_offers_response.data

        # 호텔 목록 표시 및 지역 버튼 추가
        display_hotels(hotels, iata_code)
    except ResponseError as error:
        messagebox.showerror("Error", "Failed to fetch hotels: " + str(error))

# 호텔 목록 표시 및 지역 버튼 추가 함수
def display_hotels(hotels, iata_code):
    # 호텔 목록 표시를 위한 프레임 생성
    hotel_frame = tk.Frame(window)
    hotel_frame.grid(row=5, columnspan=2, padx=5, pady=5)

    # 호텔 목록을 위한 리스트박스 및 스크롤바 생성
    scrollbar = tk.Scrollbar(hotel_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    listbox = tk.Listbox(hotel_frame, yscrollcommand=scrollbar.set)
    for hotel in hotels:
        hotel_name = hotel['hotel']['name']
        hotel_price = hotel['offers'][0]['price']['total'] if 'offers' in hotel and 'price' in hotel['offers'][0] else "N/A"
        hotel_address = hotel['hotel']['address']['lines'][0] if 'address' in hotel['hotel'] and 'lines' in hotel['hotel']['address'] else "Address not available"
        hotel_info = f"{hotel_name} - {hotel_price} - {hotel_address}"
        listbox.insert(tk.END, hotel_info)
    listbox.pack(side=tk.LEFT, fill=tk.BOTH)
    scrollbar.config(command=listbox.yview)

    # 지역 버튼 생성
    if iata_code in regions:
        row = 6
        for region_name, coords in regions[iata_code].items():
            region_button = ttk.Button(window, text=region_name, command=lambda rn=region_name: sort_hotels(hotels, rn, listbox))
            region_button.grid(row=row, column=0, padx=5, pady=5)
            row += 1

# 호텔 정렬 및 표시 함수
def sort_hotels(hotels, region_name, listbox):
    region_coords = regions[combo_iata.get()][region_name]

    # 거리 계산 함수 (헤버사인 공식 사용)
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371  # 지구의 반경(km)
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        a = math.sin(delta_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    # 호텔 위치 정보가 없는 경우에 대한 예외 처리
    def get_hotel_coords(hotel):
        if 'latitude' in hotel['hotel'] and 'longitude' in hotel['hotel']:
            return hotel['hotel']['latitude'], hotel['hotel']['longitude']
        else:
            return None, None  # 좌표 정보가 없는 경우 None 반환

    # 호텔을 지역에 따라 정렬
    sorted_hotels = []
    for hotel in hotels:
        lat, lon = get_hotel_coords(hotel)
        if lat is not None and lon is not None:
            hotel['distance'] = haversine(region_coords['lat'], region_coords['lon'], lat, lon)
            sorted_hotels.append(hotel)
    sorted_hotels.sort(key=lambda x: x['distance'])

    # 리스트박스 업데이트
    listbox.delete(0, tk.END)
    for hotel in sorted_hotels:
        hotel_name = hotel['hotel']['name']
        hotel_price = hotel['offers'][0]['price']['total'] if 'offers' in hotel and 'price' in hotel['offers'][0] else "Price not available"
        hotel_address = hotel['hotel']['address']['lines'][0] if 'address' in hotel['hotel'] and 'lines' in hotel['hotel']['address'] else "Address not available"
        hotel_info = f"{hotel_name} - {hotel_price} - {hotel_address}"
        listbox.insert(tk.END, hotel_info)


# 메인 루프
window.mainloop()
