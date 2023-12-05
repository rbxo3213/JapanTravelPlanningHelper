
# JTPH - Japan Travel Planning Helper

The JTPH (Japan Travel Planning Helper) is a Python-based tool developed by a student for educational purposes. It is designed to assist in planning travels to Japan by providing essential information about various destinations, including airports, hotels, points of interest, and transportation options.

## Features

- **Airport Search**: Find airport details based on IATA codes using `iataSearcher.py`.
- **Hotel Search**: Locate hotels in different regions with `HotelSearcher.py`.
- **Region Information**: Access information about various regions in Japan from `regions.json`.
- **Transportation Details**: Get details on transportation options from `transport_info.json`.
- **Points of Interest**: Explore points of interest in Japanese destinations with `pois.json`.

## Data Files

The program utilizes several JSON files stored in the `JSON` directory, including `airports.json`, `pois.json`, `regions.json`, and `transport_info.json`.

## Usage

1. Clone or download the repository to your local machine.
2. Ensure Python 3.x is installed on your system.
3. Run the `JTPH.py` script:

    ```bash
    python JTPH.py
    ```

4. Follow the prompts to input your travel preferences and details.

## Project Structure

- `JSON/`: Contains all the JSON data files.
- `Searchers/`: Includes Python scripts for searching hotels and airports.
- `JTPH.py`: The main script to start the program.
- `SelectionManager.py`: Manages user selections within the program.

## Educational Purpose

This project is developed as part of my learning journey in Python programming. It is intended for educational use and personal project development.

## Support

For any questions or support, please open an issue in the repository or contact me directly.
