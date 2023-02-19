import os.path
import sys
import time

import pandas
from bs4 import BeautifulSoup
from IPython.core.display import display
from datetime import datetime, timedelta
import pandas as pd
import requests
import json


def get_html(data, date, departure, departure_id, arrival, arrival_id, bc_number):
    retry_count = 0
    max_retries = 5

    while retry_count < max_retries:
        try:
            data = data.format(departure, departure_id, arrival, arrival_id, date, bc_number)
            request = requests.post(url, data=data)
            return request.text
        except requests.exceptions.ConnectionError as e:
            retry_count += 1
            # Wait for 5 seconds before retrying
            print("An error occurred, trying again. {}/{} retries".format(retry_count, max_retries))
            time.sleep(5)
            if retry_count == max_retries:
                # Raise the exception if the maximum number of retries has been reached
                raise e


def get_prices(prices_html):
    temp_prices = []
    for slot in prices_html:
        price = slot.find('div', class_='tbpSlotPrice')
        if not price:
            temp_prices.append(None)
            continue
        price = price.text.strip()
        price = price.split("\n")[1].strip()  # Remove the unwanted text
        price = price.replace("\xa0€", "").strip()  # Remove the whitespace and currency symbol
        price = float(price.replace(",", "."))  # Replace the comma with a dot for floating-point numbers
        temp_prices.append(price)
    print(temp_prices)
    return temp_prices


def save_data(prices, departure, arrival, date, bc_number):
    prices.append(departure)
    prices.append(arrival)
    prices.append(date)
    prices.append(datetime.now().strftime('%d.%m.%Y'))
    prices.append(bc_number)
    return prices


def init():
    with open('stations.json', 'r') as stations_file:
        stations = json.load(stations_file)

    start(stations["departures"], stations["arrivals"])
    start(stations["arrivals"], stations["departures"])


def start(departures, arrivals):
    for bahn_card in range(0, 2):
        prices_list = []
        for arrival_stations in arrivals:
            for departure_station in departures:
                for days in range(1, 22):
                    retry_count = 0
                    max_retries = 15
                    date = (datetime.now() + timedelta(days=days)).strftime('%d.%m.%Y')
                    print(date, departure_station["name"], arrival_stations["name"])
                    while retry_count < max_retries:
                        html_text = get_html(
                            dataArray[0],
                            date,
                            departure_station["name"],
                            departure_station["id"],
                            arrival_stations["name"],
                            arrival_stations["id"],
                            bahn_card
                        )
                        soup = BeautifulSoup(html_text, 'lxml')
                        # from_field = soup.find_all('div', id='tbpSlotContainer')
                        prices_html = soup.find_all('div', class_='tbpSlot')
                        html_prices = get_prices(prices_html)
                        if html_prices:
                            prices_list.append(save_data(html_prices, departure_station["name"], arrival_stations["name"], date, bahn_card))
                            print("-----------------------------------------------")
                            break
                        retry_count += 1
                        print('Data missing. {}/{} retries'.format(retry_count, max_retries))
                        time.sleep(2.5)
                        if retry_count == max_retries:
                            sys.exit('Too many retries. Exiting program.')
        for x in prices_list:
            print(x)
        save_to_parquet(prices_list)


def save_to_parquet(prices_list):
    prices_df = pd.DataFrame(prices_list)
    prices_df.columns = {'0-7': float, '7-10': float, '10-13': float, '13-16': float, '16-19': float, '19-0': float,
                         'departure': str, 'arrival': str, 'travel_date': datetime, 'scanned_at': datetime,
                         'bahn_card': int
                         }
    prices_df['travel_date'] = pd.to_datetime(prices_df['travel_date'], format='%d.%m.%Y')
    prices_df['scanned_at'] = pd.to_datetime(prices_df['scanned_at'], format='%d.%m.%Y')
    prices_df.info()

    if not os.path.exists('data.parquet'):
        prices_df.to_parquet('data.parquet')
    else:
        loaded_data = pd.read_parquet('data.parquet')
        combined_data = pd.concat([loaded_data, prices_df], ignore_index=True)
        combined_data.to_parquet('data.parquet')
        display(combined_data)


url = 'https://reiseauskunft.bahn.de/bin/query.exe/dn?ld=4314&country=DEU&protocol=https:&rt=1&OK='
dataArray = [
    'HWAI%3DQUERY%21rit=no&queryPageDisplayed=yes&HWAI%3DQUERY%21displayed=yes&HWAI%3DJS%21ajax=yes&HWAI%3DJS%21js' \
    '=yes&REQ0JourneyStopsS0A=255&REQ0JourneyStopsS0G={}&REQ0JourneyStopsS0ID={}' \
    '&REQ0JourneyStopsS0a=131072&REQ0JourneyStopsZ0A=255&REQ0JourneyStopsZ0G={}' \
    '&REQ0JourneyStopsZ0ID={}&REQ0JourneyDate={}&REQ0JourneyTime=14%3A00' \
    '&REQ0HafasSearchForw=1&REQ1JourneyDate=&REQ1JourneyTime=&REQ1HafasSearchForw=1&useFastConnectionsOnly=on&HWAI' \
    '%3DQUERY%24PRODUCTS%240_0%21show=yes&traveller_Nr=1&REQ0Tariff_TravellerType.1=Y' \
    '&REQ0Tariff_TravellerReductionClass.1={}&REQ0Tariff_TravellerAge.1=&REQ0Tariff_Class=2&REQ0HafasChangeTime=0' \
    '%3A1&HWAI%3DQUERY%24via%240%21number=0&REQ0JourneyStops1ID=&REQ0JourneyStops2ID=&HWAI%3DQUERY%24via%241' \
    '%21number=0&REQ1JourneyStops1ID=&REQ1JourneyStops2ID=&REQ0JourneyRevia=yes&HWAI%3DQUERY%21prodAdvanced=0' \
    '&existOptimizePrice=1&useFastConnectionsOnly=on&existProductNahverkehr=1&HWAI%3DQUERY%24PRODUCTS%240_0%21show' \
    '=yes&HWAI%3DQUERY%24PRODUCTS%240_0%21show=yes&advancedProductMode=yes&REQ0JourneyProduct_prod_section_0_0=1' \
    '&REQ0JourneyProduct_prod_section_0_1=1&REQ0JourneyProduct_prod_section_0_2=1' \
    '&REQ0JourneyProduct_prod_section_0_3=1&REQ0JourneyProduct_prod_section_0_4=1' \
    '&REQ0JourneyProduct_prod_section_0_5=1&REQ0JourneyProduct_prod_section_0_6=1' \
    '&REQ0JourneyProduct_prod_section_0_7=1&REQ0JourneyProduct_prod_section_0_8=1' \
    '&REQ0JourneyProduct_prod_section_0_9=1&REQ0JourneyProduct_opt_section_0_list=0%3A0000' \
    '&existIntermodalDep_enable=yes&REQ0JourneyDep__enable=Foot&existIntermodalDest_enable=yes' \
    '&REQ0JourneyDest__enable=Foot&HWAI%3DQUERY%21hideExtInt=no&REQ0JourneyDep_Foot_minDist=0' \
    '&REQ0JourneyDest_Foot_minDist=0&REQ0JourneyDep_Foot_maxDist=2000&REQ0JourneyDest_Foot_maxDist=2000' \
    '&REQ0JourneyDep_Bike_minDist=0&REQ0JourneyDest_Bike_minDist=0&REQ0JourneyDep_Bike_maxDist=5000' \
    '&REQ0JourneyDest_Bike_maxDist=5000&REQ0JourneyDep_KissRide_minDist=2000&REQ0JourneyDest_KissRide_minDist=2000' \
    '&REQ0JourneyDep_KissRide_maxDist=50000&REQ0JourneyDest_KissRide_maxDist=50000&existOptionBits=yes' \
    '&existTbpMode=1&tbpMode=1&rtMode=12&start=Suchen'
]
init()
