import sys
import pysqlite3
sys.modules["sqlite3"] = pysqlite3

import functions_framework
from time import sleep
import pandas as pd
import requests
from keys import MySQL_pass, AeroDatabox

PUBLIC_IP = "your-cloud-sql-public-ip"
DB_NAME = "gans_local"


def request_airports_data(cities: list[str], connection_string: str) -> None:
    cities_df = pd.read_sql('cities', con=connection_string)

    airports_data = []

    for city in cities:
        row = cities_df.loc[cities_df['city'] == city].iloc[0]
        city_id = row["city_id"]

        url = "https://aerodatabox.p.rapidapi.com/airports/search/location"
        params = {
            "withFlightInfoOnly": "true",
            "lat": row['latitude'],
            'lon': row['longitude'],
            'radiusKm': "50",
            'limit': 10
        }
        headers = {
            "X-RapidAPI-Key": AeroDatabox,
            "X-RapidAPI-Host": "aerodatabox.p.rapidapi.com",
        }

        sleep(5)
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        airports_json = response.json()

        for airport in airports_json['items']:
            airport_data = {
                'city_id': city_id,
                'icao': airport['icao'],
                'municipality_name': airport['municipalityName']
            }
            airports_data.append(airport_data)

    airports_df = pd.DataFrame(airports_data)
    airports_df.to_sql('airports', if_exists='append', con=connection_string, index=False)


@functions_framework.http
def main(request):
    connection_string = f"mysql+pymysql://root:{MySQL_pass}@{PUBLIC_IP}:3306/{DB_NAME}"
    cities_list = ["Istanbul", "Antalya"]
    request_airports_data(cities_list, connection_string)
    return "Airports table is updated.", 200
