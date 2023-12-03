# base_application.py
import json
from amadeus import Client

class BaseApplication:
    def __init__(self):
        self.amadeus = self.initialize_amadeus_client()

    def initialize_amadeus_client(self):
        with open('API_key.json', 'r') as file:
            api_keys = json.load(file)
        return Client(client_id=api_keys['AMADEUS_API_KEY'], client_secret=api_keys['AMADEUS_API_SECRET'])

    @staticmethod
    def convert_iata_code(iata_code):
        if iata_code in ['HND', 'NRT']:
            return 'TYO'
        return iata_code

    @staticmethod
    def convert_price(price, conversion_rate=1350):
        return int(float(price) * conversion_rate)

    @staticmethod
    def convert_duration(duration):
        try:
            hours = int(duration[2:duration.find('H')])
            minutes = int(duration[duration.find('H')+1:duration.find('M')])
            return f"{hours}h {minutes}m"
        except ValueError:
            return duration
