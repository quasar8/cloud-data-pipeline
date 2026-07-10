import sys
import pysqlite3
sys.modules["sqlite3"] = pysqlite3
import functions_framework
from time import sleep
from datetime import datetime, timedelta
import datetime as dt
import pandas as pd
import requests
from pytz import timezone
from keys import MySQL_pass, AeroDatabox

PUBLIC_IP = "your-cloud-sql-public-ip"
DB_NAME = "gans_local"


def request_flights_data(connection_string: str) -> None:
    berlin_timezone = timezone('Europe/Berlin')
    airports_df = pd.read_sql('airports', con=connection_string)

    flights_data = []

    tomorrow = dt.datetime.now(timezone('Europe/Berlin')) + dt.timedelta(days=1)
    tomorrow_date = tomorrow.strftime('%Y-%m-%d')
    morning_start = f'{tomorrow_date}T00:00'
    morning_end = f'{tomorrow_date}T11:59'
    afternoon_start = f'{tomorrow_date}T12:00'
    afternoon_end = f'{tomorrow_date}T23:59'
    day_parts = [(morning_start, morning_end), (afternoon_start, afternoon_end)]

    for _, row in airports_df.iterrows():
        for time_start, time_end in day_parts:
            base_url = "https://aerodatabox.p.rapidapi.com/flights/airports"
            path_params = f"/icao/{row['icao']}/{time_start}/{time_end}"
            full_url = base_url + path_params
            params = {
                'withLeg': True,
                'direction': 'Arrival',
                'withCancelled': False,
                'withCodeshared': False,
                'withCargo': False,
                'withPrivate': False,
                'withLocation': False
            }
            headers = {
                "X-RapidAPI-Key": AeroDatabox,
                "x-rapidapi-host": "aerodatabox.p.rapidapi.com",
            }

            sleep(5)
            response = requests.get(full_url, headers=headers, params=params)
            if response.status_code == 200:
                flights_json = response.json()
                retrieval_time = datetime.now(berlin_timezone).strftime("%Y-%m-%d %H:%M:%S")

                for flight in flights_json['arrivals']:
                    flight_item = {
                        "arrival_airport_icao": row['icao'],
                        "departure_airport_icao": flight.get("departure", {}).get("airport", {}).get("icao", None),
                        "departure_airport_name": flight.get("departure", {}).get("airport", {}).get("name", None),
                        "scheduled_arrival_time": flight.get("arrival", {}).get("scheduledTime", {}).get("local", None),
                        "flight_number": flight.get("number", None),
                        "data_retrieved_at": retrieval_time
                    }
                    flights_data.append(flight_item)
            else:
                print(response.status_code, "code for", row['icao'])

    flights_df = pd.DataFrame(flights_data)
    flights_df["scheduled_arrival_time"] = flights_df["scheduled_arrival_time"].str[:-6]
    flights_df["scheduled_arrival_time"] = pd.to_datetime(flights_df["scheduled_arrival_time"])
    flights_df["data_retrieved_at"] = pd.to_datetime(flights_df["data_retrieved_at"])

    try:
        flights_df.to_sql('flights', if_exists='append', con=connection_string, index=False)
    except Exception as e:
        print(type(e).__name__)
        print(e)


@functions_framework.http
def main(request):
    connection_string = f"mysql+pymysql://root:{MySQL_pass}@{PUBLIC_IP}:3306/{DB_NAME}"
    request_flights_data(connection_string)
    return "Flights table is updated.", 200
