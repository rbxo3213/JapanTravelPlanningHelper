import requests
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import tkcalendar as cal

# 여기에 실제 Amadeus API 키와 시크릿을 입력하세요.
API_KEY = 'cOusKkB4qE2sAtu5yLessWsc0k6HgRwc'
API_SECRET = 'ZKk8GXjrsBkNXiKf'

# 액세스 토큰을 가져오는 함수
def get_access_token():
    auth_url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    auth_data = {
        'grant_type': 'client_credentials',
        'client_id': 'cOusKkB4qE2sAtu5yLessWsc0k6HgRwc',
        'client_secret': 'ZKk8GXjrsBkNXiKf'
    }
    response = requests.post(auth_url, data=auth_data)
    return response.json().get('access_token')

def fetch_airports(access_token):
    """일본 공항 목록을 가져오는 함수"""
    try:
        destinations_url = "https://test.api.amadeus.com/v1/shopping/flight-destinations"
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        params = {
            'origin': 'TYO'  # 예시로 도쿄를 사용
        }
        response = requests.get(destinations_url, headers=headers, params=params)

        print(f"Response Status: {response.status_code}")
        print(f"Response Content: {response.content}")

        if response.status_code == 200:
            # 목적지의 'destination' 값을 추출
            return [destination['destination'] for destination in response.json().get('data', [])]
        else:
            print("Failed to fetch destinations")
            return []
    except Exception as e:
        print(f"Error occurred: {e}")
        return []


# 실제 항공권 정보를 가져오는 함수
def fetch_flight_info(access_token, origin, destination, departure_date, return_date):
    flights_url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    params = {
        'originLocationCode': origin,
        'destinationLocationCode': destination,
        'departureDate': departure_date,
        'returnDate': return_date,
        'adults': '1',
        'max': '3'  # 최대 3개의 결과를 가져옵니다.
    }
    response = requests.get(flights_url, headers=headers, params=params)
    return response.json().get('data', [])  # 'data' 키에 실제 항공권 정보가 포함됩니다.

def get_japanese_airports():
    # 일본 공항 IATA 코드 목록
    japanese_airports = ['HND', 'NRT', 'KIX', 'ITM', 'CTS', 'FUK', 'OKA', 'NGO', 'HIJ', 'SDJ']
    return japanese_airports

# 일본 여행 도우미 앱 클래스
class JapanTravelHelperApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Japan Travel Planning Helper')
        self.geometry('600x500')
        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        # 출발지 선택기 추가
        self.initialize_origin_selector()
        
        # 도착지 선택기 추가
        self.initialize_destination_selector()
        
        # 날짜 선택기 추가
        self.initialize_date_selectors()

        # 검색 및 종료 버튼 추가
        self.initialize_search_quit_buttons()

    def initialize_origin_selector(self):
        origin_label = ttk.Label(self, text='Choose your departure airport:', font=('Helvetica', 10))
        origin_label.pack(pady=10)
        
        # 출발지 선택 콤보박스
        self.origin_var = tk.StringVar()
        origin_combobox = ttk.Combobox(self, textvariable=self.origin_var, values=['ICN'], width=47)
        origin_combobox.pack(pady=10)

    def initialize_destination_selector(self):
        # 목적지 선택을 위해 공항 목록을 가져오는 코드를 추가
        access_token = get_access_token()
        if access_token:
            airports = fetch_airports(access_token)
        else:
            airports = []

        destination_label = ttk.Label(self, text='Choose your destination in Japan:', font=('Helvetica', 10))
        destination_label.pack(pady=10)

        # 목적지 선택 콤보박스
        self.destination_var = tk.StringVar()
        destination_combobox = ttk.Combobox(self, textvariable=self.destination_var, values=airports, width=47)
        destination_combobox.pack(pady=10)

    def initialize_date_selectors(self):
        date_frame = ttk.Frame(self)  # 출발일과 귀국일 선택기를 담을 프레임 생성
        date_frame.pack(pady=20)

        # 출발일 선택기
        departure_date_label = ttk.Label(date_frame, text='Choose your departure date:', font=('Helvetica', 10))
        departure_date_label.grid(row=0, column=0, padx=10, pady=10)  # 레이블을 첫 번째 열에 배치
        self.departure_date_calendar = cal.Calendar(date_frame, selectmode='day')
        self.departure_date_calendar.grid(row=1, column=0, padx=10)  # 캘린더를 첫 번째 열에 배치
    
        # 귀국일 선택기
        return_date_label = ttk.Label(date_frame, text='Choose your return date:', font=('Helvetica', 10))
        return_date_label.grid(row=0, column=1, padx=10, pady=10)  # 레이블을 두 번째 열에 배치
        self.return_date_calendar = cal.Calendar(date_frame, selectmode='day')
        self.return_date_calendar.grid(row=1, column=1, padx=10)  # 캘린더를 두 번째 열에 배치


    def initialize_search_quit_buttons(self):
        # 검색 버튼
        search_button = ttk.Button(self, text='Search', command=self.on_search)
        search_button.pack(pady=10)

        # 종료 버튼
        quit_button = ttk.Button(self, text='Quit', command=self.destroy)
        quit_button.pack(side='right', padx=10, pady= 10)

    def on_search(self, event=None):
        # 검색 버튼 누를 때의 행동, 날짜를 캘린더 위젯에서 가져옴
        access_token = get_access_token()
        if access_token:
            origin = self.origin_var.get()
            destination = self.destination_var.get()
            departure_date = self.departure_date_calendar.get_date()
            return_date = self.return_date_calendar.get_date()
            if origin and destination and departure_date and return_date:
                flights = fetch_flight_info(access_token, origin, destination, departure_date, return_date)
                self.display_flights(flights)
            else:
                messagebox.showerror("Error", "Please enter all fields correctly.")
        else:
            messagebox.showerror("Error", "Failed to get access token.")

    def display_flights(self, flights):
        # 새로운 윈도우를 생성하여 결과를 표시합니다.
        result_window = tk.Toplevel(self)
        result_window.title('Flight Results')

        for flight in flights:
            flight_info = f"Departure: {flight['itineraries'][0]['segments'][0]['departure']['iataCode']} on {flight['itineraries'][0]['segments'][0]['departure']['at']}\n"
            flight_info += f"Arrival: {flight['itineraries'][0]['segments'][-1]['arrival']['iataCode']} on {flight['itineraries'][0]['segments'][-1]['arrival']['at']}\n"
            flight_info += f"Price: {flight['price']['total']} {flight['price']['currency']}\n"

            label = ttk.Label(result_window, text=flight_info, font=('Helvetica', 10))
            label.pack()

        if not flights:
            label = ttk.Label(result_window, text="No flights found.", font=('Helvetica', 10))
            label.pack()

def main():
    app = JapanTravelHelperApp()
    app.mainloop()

if __name__ == "__main__":
    main()
