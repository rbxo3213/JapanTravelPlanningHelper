import tkinter as tk
from tkinter import ttk, messagebox
import openai

class SelectionManager:
    def __init__(self, root, origin_var, destination_var, adults_var, departure_calendar, return_calendar, gpt_api_key):
        self.root = root
        self.GPT_API = gpt_api_key
        self.selected_flight = None
        self.selected_hotel = None
        self.selected_pois = []
        self.selected_transport = None
        self.selected_pass_names = []
        self.selected_durations = []
        self.origin_var = origin_var
        self.destination_var = destination_var
        self.adults_var = adults_var
        self.departure_calendar = departure_calendar
        self.return_calendar = return_calendar

        # 선택 항목을 표시할 프레임 생성
        self.selection_frame = ttk.LabelFrame(root, text="Current Selections", padding=(20, 10))
        self.selection_frame.grid(row=6, column=0, columnspan=2, sticky="ew")

        # 선택 항목을 표시할 레이블 생성
        self.flight_label = ttk.Label(self.selection_frame, text="")
        self.flight_label.pack()

        self.hotel_label = ttk.Label(self.selection_frame, text="")
        self.hotel_label.pack()

        self.pois_label = ttk.Label(self.selection_frame, text="")
        self.pois_label.pack()

        # Transport 레이블을 생성하고 설정합니다.
        self.transport_label = ttk.Label(self.selection_frame, text="")
        self.transport_label.pack()

        # 리셋 버튼 생성
        self.reset_button = ttk.Button(self.selection_frame, text="Reset", command=self.reset_selections)
        self.reset_button.pack()

        # OK 버튼 생성 및 command 설정 변경
        self.ok_button = ttk.Button(self.selection_frame, text="Make Plan", command=self.confirm_and_generate_plan)
        self.ok_button.pack()

    def update_flight(self, flight_info):
        # Assuming flight_info is a dictionary with the necessary information
        formatted_flight_details = (
            f"Flight: Destination: {flight_info['destination']}, "
            f"Price: {flight_info['price']} KRW, \n"
            f"Departure: {flight_info['departure_time']}, "
            f"Arrival: {flight_info['arrival_time']}"
        )
        self.selected_flight = formatted_flight_details
        self.flight_label.config(text=formatted_flight_details)

    def update_hotel(self, hotel_info):
        self.selected_hotel = hotel_info
        self.hotel_label.config(text=f"{hotel_info}")

    def add_poi(self, poi_info):
        # If the POI is not already selected, append it to the list
        if poi_info not in self.selected_pois:
            self.selected_pois.append(poi_info)
            # Update the POIs label with each POI on a new line
            pois_text = "\n".join(self.selected_pois)
            self.pois_label.config(text=f"{pois_text}")

    def update_transport(self, pass_name=None, duration=None):
        if pass_name:
            self.selected_pass_names = [pass_name]  # 현재 pass_name으로 리스트를 대체
        if duration:
            self.selected_durations = [duration]  # 현재 duration으로 리스트를 대체
        # PassName과 Duration을 함께 출력
        self.transport_label.config(text=f"PassName: {', '.join(self.selected_pass_names)}, Duration: {', '.join(self.selected_durations)}")


    def reset_selections(self):
        self.selected_flight = None
        self.selected_hotel = None
        self.selected_pois = []
        self.selected_transport = None
        self.flight_label.config(text="")
        self.hotel_label.config(text="")
        self.pois_label.config(text="")
        self.transport_label.config(text="")

    def confirm_selections(self):
        # 선택 확인 로직
        # 예를 들어, 선택 사항을 파일로 저장하거나 다른 프로세스에 전달할 수 있습니다.
        print(f"Confirmed selections: {self.selected_flight}, {self.selected_hotel}, {self.selected_pois}, {self.selected_transport}")

    def generate_travel_plan(self):
        # Construct the prompt for GPT-3
        travel_details = f"Travel to {self.destination_var.get()} from {self.origin_var.get()} for {self.adults_var.get()} adults. " \
                         f"Departure on {self.departure_calendar.get_date()} and return on {self.return_calendar.get_date()}. " \
                         f"Includes flight: {self.selected_flight}, hotel: {self.selected_hotel}, " \
                         f"POIs: {', '.join(self.selected_pois)}, " \
                         f"Transport: {', '.join(self.selected_pass_names)}, Duration: {', '.join(self.selected_durations)}. " \
                         "Please suggest a travel plan."
    
        try:
            # Updated API call
            from openai import OpenAI
            client = OpenAI(api_key=self.GPT_API)
            response = client.chat.completions.create(
                messages=[{
                    "role": "system",
                    "content": travel_details
                }],
                model="gpt-3.5-turbo"
            )
            # Displaying the result in a new window
            result_window = tk.Toplevel(self.root)
            result_window.title("Travel Plan Suggestion")
            result_window.geometry("600x400")
    
            result_text = tk.Text(result_window, wrap="word")
            if response.choices and response.choices[0].message:
                result_text.insert("1.0", response.choices[0].message.content)
            result_text.pack(expand=True, fill="both")
    
        except Exception as e:  # Generic exception handling, consider specifying exact exceptions
            messagebox.showerror("Error", f"An error occurred while generating the travel plan: {e}")


    def get_selections(self):
        # 사용자가 선택한 모든 정보를 반환
        return {
            'flight': self.selected_flight,
            'hotel': self.selected_hotel,
            'pois': self.selected_pois,
            'transport': {
                'pass_names': self.selected_pass_names,
                'durations': self.selected_durations
            }
        }
        
    def confirm_and_generate_plan(self):
        self.confirm_selections()
        self.generate_travel_plan()