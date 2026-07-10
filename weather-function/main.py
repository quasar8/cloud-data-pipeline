import sys
import pysqlite3
sys.modules["sqlite3"] = pysqlite3

import functions_framework
import datetime as dt
import pandas as pd
import requests
from pytz import timezone
from keys import MySQL_pass, OW_API_key

PUBLIC_IP = "your-cloud-sql-public-ip"
DB_NAME = "gans_local"


def update_weather_table(connection_string: str) -> None:
    cities_df = pd.read_sql('cities', con=connection_string)

    forecasts = []

    for _, row in cities_df.iterrows():
        lat = row['latitude']
        long = row['longitude']

        params = {
            'lat': lat,
            'lon': long,
            'appid': OW_API_key,
            'units': "metric",
        }
        response = requests.get(url='https://api.openweathermap.org/data/2.5/forecast?', params=params)
        weather_data = response.json()

        retrieval_time = (dt.datetime
                          .now(timezone('Europe/Berlin'))
                          .strftime("%Y-%m-%d %H:%M:%S"))

        for forecast in weather_data['list']:
            forecast_dict = {
                'city_id': row['city_id'],
                'forecast_time': forecast.get("dt_txt"),
                "outlook": forecast["weather"][0].get("description", None),
                'temperature': forecast["main"].get("temp"),
                'rain_in_last_3h': forecast.get('rain', {'3h': 0})['3h'],
                "wind_speed": forecast["wind"].get("speed"),
                "rain_prob": forecast.get("pop", None),
                "data_retrieved_at": retrieval_time,
            }
            forecasts.append(forecast_dict)

    weather_df = pd.DataFrame(forecasts)
    weather_df["forecast_time"] = pd.to_datetime(weather_df["forecast_time"])
    weather_df["data_retrieved_at"] = pd.to_datetime(weather_df["data_retrieved_at"])
    weather_df.to_sql('weather', if_exists='append', con=connection_string, index=False)


@functions_framework.http
def main(request):
    connection_string = f"mysql+pymysql://root:{MySQL_pass}@{PUBLIC_IP}:3306/{DB_NAME}"
    update_weather_table(connection_string)
    return "Weather table is updated.", 200
