import tkinter as tk
from FlightSearch import FlightSearch
from HotelSearch import HotelSearch
from GuiApplication import GuiApplication

if __name__ == '__main__':
    root = tk.Tk()
    root.title("Travel Search Application")

    flight_search = FlightSearch()
    hotel_search = HotelSearch()
    gui_app = GuiApplication(root, flight_search, hotel_search)

    root.mainloop()
