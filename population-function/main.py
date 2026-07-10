import sys
import pysqlite3
sys.modules["sqlite3"] = pysqlite3

import functions_framework
import datetime as dt
import pandas as pd
import requests
from bs4 import BeautifulSoup
from pytz import timezone
from keys import MySQL_pass

PUBLIC_IP = "your-cloud-sql-public-ip"
DB_NAME = "gans_local"


def scrape_and_send_population_data(connection_string: str) -> None:
    cities_table = pd.read_sql('cities', con=connection_string)

    populations_data = []

    for city in cities_table['city']:
        url = f"https://www.wikipedia.org/wiki/{city}"
        headers = {'User-Agent': 'Chrome/134.0.0.0'}

        response = requests.get(url, headers=headers)
        city_soup = BeautifulSoup(response.content, 'html.parser')

        city_population = city_soup.find(string="Population").find_next("td").get_text()
        city_population_clean = int(city_population.replace(",", ""))

        timestamp = (dt.datetime
                     .now(timezone('Europe/Berlin'))
                     .strftime("%Y-%m-%d %H:%M:%S"))

        populations_data.append({
            "city": city,
            "population": city_population_clean,
            "timestamp_population": timestamp
        })

    populations_df = pd.DataFrame(populations_data)

    city_populations_df = (
        populations_df
        .merge(cities_table, on='city', how='inner')
        [['city_id', 'population', 'timestamp_population']]
    )

    city_populations_df.to_sql('population', if_exists='append', con=connection_string, index=False)


@functions_framework.http
def main(request):
    connection_string = f"mysql+pymysql://root:{MySQL_pass}@{PUBLIC_IP}:3306/{DB_NAME}"
    scrape_and_send_population_data(connection_string)
    return "Population table is updated.", 200
