
## Features

- **Search for flights and accommodation**: Intuitive interface for choosing flights and hotels, showing real-time prices and availability loaded through Amadeus api.
- **Find points of interest**: Add a itinerary with a tour of various attractions and attractions across Japan.
- **Transport information**: Informs the coverage and duration option of the transport pass ticket available in the area.
- **Search for IATA codes**: The 'iataSearcher.py ' tool is independent of the functionality of JTPH, but it is a program that outputs IATA codes when you enter city names around the world, and is suitable for developers who want to expand the functionality of the program by providing IATA codes for cities other than Japan, such as Berlin, New York, and Paris.

## Installation & Settings

Replicate the repository and make sure Python 3.x is installed. Go to the project directory and install the required dependencies.

## Usage

1. **Start the program**: Run the application by running 'JTPH.py '.
<img width="252" alt="스크린샷 2023-12-05 173157" src="https://github.com/rbxo3213/JapanTravelPlanningHelper/assets/42289726/4348e458-525b-4653-85a4-7d6048c66855">
3. **Start screen**: Select the departure point, destination, departure date, return date, and number of people and press the search button. The return selection window shows the selected airline, hotel, pois, and transportation information.
4. **Select tickets**: List tickets available for booking by price. Select tickets.
5. **Hotel Selection**: List a list of hotels (name, price) available for booking. Once you have selected a location, the list of hotels will be sorted by the one you have selected. Please select a hotel.
3. **Explore points of interest**: Scroll through the list of attractions in the area you're traveling to and add them to your plan.
4. **Transport option review**: Select the available transport pass and duration of use in the area you are traveling to.
5. **Manage options**: You can reset selected elements by pressing the reset button on the start screen. Press the close all window button to close all search windows.
6. Once you've selected the air, hotel, attraction, and transportation you want, press the Make Plan button to get travel planning suggestions.

## Additional Notes

'iataSearcher.py ' is a reference and assistance tool for those interested in adding features for international travel using amadeus api.

'SelectionManager.py ' is critical to OpenAI's interface with A OpenAI, which generates travel plans based on user selection.

## Support

Please open the issue in the repository for support or questions.
