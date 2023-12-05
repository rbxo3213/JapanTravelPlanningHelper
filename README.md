# JTPH - Japan Travel Planning Helper

- Project Description
  - The JTPH (Japan Travel Planning Helper) is a Python-based tool developed by a student for educational purposes. It is designed to assist in planning travels to Japan by providing essential information about various destinations, including airports, hotels, points of interest, and transportation options.
- Educational Purpose
  - This project is developed as part of my learning journey in Python programming. It is intended for educational use and personal project development.

## Development Environment

- Python 3.10.10
- Visual Studio Code 1.62.3
- Amadeus API
- OpenAI API

## Data Files

The program utilizes several JSON files stored in the `JSON` directory, including `airports.json`, `pois.json`, `regions.json`, and `transport_info.json`.

## Features

- **Search for flights and accommodation**: Intuitive interface for choosing flights and hotels, showing real-time prices and availability loaded through Amadeus api.
- **Find points of interest**: Add a itinerary with a tour of various attractions and attractions across Japan.
- **Transport information**: Informs the coverage and duration option of the transport pass ticket available in the area.
- **Search for IATA codes**: The 'iataSearcher.py ' tool is independent of the functionality of JTPH, but it is a program that outputs IATA codes when you enter city names around the world, and is suitable for developers who want to expand the functionality of the program by providing IATA codes for cities other than Japan, such as Berlin, New York, and Paris.

## Installation & Settings

Replicate the repository and make sure Python 3.x is installed. Go to the project directory and install the required dependencies.

## Usage

0. **Install required dependencies**:

```bash
pip install -r requirements.txt
```

- **It's important** And please make and add your Amadeus API key, OpenAI API key json file named, "API_key.json", "gpt_api.json" in JSON folder 

1. **Start the program**:

```bash
python JTPH.py
```

- Run the application by running 'JTPH.py '.

2. **Start screen**: - Select the departure point, destination, departure date, return date, and number of people and press the search button. The return selection window shows the selected airline, hotel, pois, and transportation information.

   <img width="252" alt="스크린샷 2023-12-05 173157" src="https://github.com/rbxo3213/JapanTravelPlanningHelper/assets/42289726/4348e458-525b-4653-85a4-7d6048c66855">

4. **Select tickets**: - List tickets available for booking by price. Select tickets.

<img width="765" alt="스크린샷 2023-12-05 173314" src="https://github.com/rbxo3213/JapanTravelPlanningHelper/assets/42289726/7568e29e-f030-477e-88d1-7cca39feb958">

6. **Hotel Selection**: - List a list of hotels (name, price) available for booking. Once you have selected a location, the list of hotels will be sorted by the one you have selected. Please select a hotel.

<img width="438" alt="스크린샷 2023-12-05 173323" src="https://github.com/rbxo3213/JapanTravelPlanningHelper/assets/42289726/40b18402-6690-4a90-a4b7-94ffe66a14ce">

8. **Explore points of interest**: - Scroll through the list of attractions in the area you're traveling to and add them to your plan.

<img width="418" alt="스크린샷 2023-12-05 173329" src="https://github.com/rbxo3213/JapanTravelPlanningHelper/assets/42289726/eb002a5b-5d35-4d19-abb5-2c9cf7204e6a">

10. **Transport option review**: - Select the available transport pass and duration of use in the area you are traveling to.

<img width="403" alt="스크린샷 2023-12-05 173336" src="https://github.com/rbxo3213/JapanTravelPlanningHelper/assets/42289726/e2bac2dd-3020-42f5-bced-578bb9653ff0">

12. **Manage options**: - You can reset selected elements by pressing the reset button on the start screen. Press the close all window button to close all search windows.

<img width="319" alt="스크린샷 2023-12-05 173405" src="https://github.com/rbxo3213/JapanTravelPlanningHelper/assets/42289726/ef0da8b1-968b-4c09-95df-ad11d4e35b30">

14. **Automatic suggestion of travel plans**: - Once you've selected the air, hotel, attraction, and transportation you want, press the Make Plan button to get travel planning suggestions.

<img width="449" alt="스크린샷 2023-12-05 173533" src="https://github.com/rbxo3213/JapanTravelPlanningHelper/assets/42289726/1a4ae9f0-f25c-4f20-aaa8-3fb99a8f6487">

## Additional Notes

- 'iataSearcher.py ' is a reference and assistance tool for those interested in adding features for international travel using amadeus api.

<img width="110" alt="스크린샷 2023-12-05 173656" src="https://github.com/rbxo3213/JapanTravelPlanningHelper/assets/42289726/49830fe4-deba-49c9-bc6b-0e1b426d260d">

<img width="109" alt="스크린샷 2023-12-05 173641" src="https://github.com/rbxo3213/JapanTravelPlanningHelper/assets/42289726/8b65ac7e-4b95-453a-9391-bf0da5ca1ff0">

- 'SelectionManager.py ' is critical to OpenAI's interface with A OpenAI, which generates travel plans based on user selection.

- The OpenAi API used to implement the "make plan" feature consumes pre-charged money for token use, which can lead to errors if the money is exhausted.
- The Amadeus API used to implement real-time search for hotels and tickets is limited in use in Japan, so there may be cases where the search is not possible (especially hotels).

## Support

Please open the issue in the repository for support or questions.
