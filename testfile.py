import os
from amadeus import Client, ResponseError

# Load API keys from environment variables or replace 'your_api_key' and 'your_api_secret' with your actual Amadeus API credentials
AMADEUS_API_KEY = os.environ.get('AMADEUS_API_KEY', 'your_api_key')
AMADEUS_API_SECRET = os.environ.get('AMADEUS_API_SECRET', 'your_api_secret')

# Initialize Amadeus client
amadeus = Client(client_id=AMADEUS_API_KEY, client_secret=AMADEUS_API_SECRET)

def search_hotels_in_japan(city):
    try:
        # Use the Airport & City Search API to find the IATA code for the Japanese city
        city_search_response = amadeus.reference_data.locations.get(keyword=city, subType='CITY')
        city_code = city_search_response.data[0]['iataCode']  # Assuming the first result is the city we want

        # Use the Hotel Search API to find hotels in the Japanese city using the city's IATA code
        hotel_search_response = amadeus.shopping.hotel_offers.get(cityCode=city_code)
        hotels_data = hotel_search_response.data

        # Process the hotels data to display hotel names and addresses
        for hotel in hotels_data:
            print(f"Hotel Name: {hotel['hotel']['name']}")
            print(f"Hotel Address: {hotel['hotel']['address']['lines']}")
            print(f"Price: {hotel['offers'][0]['price']['total']} {hotel['offers'][0]['price']['currency']}")
            print("-" * 50)
            
    except ResponseError as error:
        print(f"An error occurred: {error}")

# Replace 'Tokyo' with the city you want to search
search_hotels_in_japan('Tokyo')
