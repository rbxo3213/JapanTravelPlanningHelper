import os
from amadeus import Client, ResponseError
import json

# API 키 파일 경로를 지정합니다.
API_KEY_FILE = 'API_key.json'

# API 키와 시크릿을 불러옵니다.
with open(API_KEY_FILE, 'r') as file:
    api_keys = json.load(file)
    API_KEY = api_keys.get('AMADEUS_API_KEY')
    API_SECRET = api_keys.get('AMADEUS_API_SECRET')


amadeus = Client(
    client_id=API_KEY,
    client_secret=API_SECRET
)

try:
    response = amadeus.shopping.flight_offers_search.get(
        originLocationCode='ICN',
        destinationLocationCode='NRT',
        departureDate='2023-12-10',
        adults=1)
    print(response.data)
except ResponseError as error:
    print(error)