import sys
import pysqlite3
sys.modules["sqlite3"] = pysqlite3

import functions_framework
import pandas as pd
import requests
from bs4 import BeautifulSoup
from lat_lon_parser import parse
from keys import MySQL_pass

PUBLIC_IP = "34.62.74.158"
DB_NAME = "gans_local"


def scrape_and_send_city_data(cities_list: list[str], connection_string: str) -> None:
    cities_data = []

    for city in cities_list:
        url = "https://en.wikipedia.org/wiki/" + city
        headers = {'User-Agent': 'Chrome/134.0.0.0'}

        response = requests.get(url, headers=headers)
        city_soup = BeautifulSoup(response.content, 'html.parser')

        country = city_soup.find(class_="infobox-data").get_text()
        lat = parse(city_soup.find('span', class_='latitude').get_text())
        long = parse(city_soup.find('span', class_='longitude').get_text())

        city_data = {
            'city': city,
            'country': country,
            'latitude': lat,
            'longitude': long,
        }
        cities_data.append(city_data)

    cities_df = pd.DataFrame(cities_data)
    cities_df.to_sql('cities', if_exists='append', con=connection_string, index=False)


@functions_framework.http
def main(request):
    connection_string = f"mysql+pymysql://root:{MySQL_pass}@{PUBLIC_IP}:3306/{DB_NAME}"
    cities_list = ["Istanbul", "Antalya"]
    scrape_and_send_city_data(cities_list, connection_string)
    return "Cities tablosu güncellendi.", 200
