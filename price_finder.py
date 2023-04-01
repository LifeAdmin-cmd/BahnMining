import os.path
import sys
import time

from bs4 import BeautifulSoup
from IPython.core.display import display
from datetime import datetime, timedelta
from math import radians, cos, sin, asin, sqrt
import pandas as pd
import numpy as np
import requests
import json


def get_html(data, travel_date, departure, departure_id, arrival, arrival_id, bc_number):
    retry_count = 0
    max_retries = 5

    while retry_count < max_retries:
        try:
            data = data.format(departure, departure_id, arrival, arrival_id, travel_date, bc_number)
            request = session.post(url, data=data)
            return request.text
        except requests.exceptions.ConnectionError as e:
            retry_count += 1
            # Wait for 5 seconds before retrying
            print("An error occurred, trying again. {}/{} retries".format(retry_count, max_retries))
            time.sleep(5)
            if retry_count == max_retries:
                # Raise the exception if the maximum number of retries has been reached
                print(e)
                raise Exception("Is Tor running?")


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


def save_data(prices, departure, arrival, travel_date, bc_number):
    prices.append(departure)
    prices.append(arrival)
    prices.append(travel_date)
    prices.append(datetime.now().strftime('%d.%m.%Y'))
    prices.append(bc_number)
    return prices


def init(starts, ends, travel_date):
    with open('stations.json', 'r') as stations_file:
        stations = json.load(stations_file)

    start(stations["departures"], stations["arrivals"])


def start(departures, arrivals, travel_date):
    for bahn_card in range(0, 2):
        prices_list = []
        for arrival_station in arrivals:
            for departure_station in departures:
                retry_count = 0
                max_retries = 15
                # date = (datetime.now() + timedelta(days=days)).strftime('%d.%m.%Y')
                print(travel_date, departure_station[0], arrival_station[0])
                while retry_count < max_retries:
                    html_text = get_html(
                        dataArray[0],
                        travel_date,
                        departure_station[0],
                        departure_station[1],
                        arrival_station[0],
                        arrival_station[1],
                        bahn_card
                    )
                    soup = BeautifulSoup(html_text, 'lxml')
                    # from_field = soup.find_all('div', id='tbpSlotContainer')
                    prices_html = soup.find_all('div', class_='tbpSlot')
                    html_prices = get_prices(prices_html)
                    if html_prices:
                        prices_list.append(save_data(html_prices, departure_station[0], arrival_station[0], travel_date, bahn_card))
                        print("-----------------------------------------------")
                        break
                    retry_count += 1
                    print('Data missing. {}/{} retries'.format(retry_count, max_retries))
                    time.sleep(2.5)
                    if retry_count == max_retries:
                        sys.exit('Too many retries. Exiting program.')


def get_tor_session():
    build_session = requests.session()
    # Tor uses the 9050 port as the default socks port
    build_session.proxies = {'http': 'socks5h://127.0.0.1:9050',
                             'https': 'socks5h://127.0.0.1:9050'}
    return build_session


def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    km = 6367 * c
    return km


def find_stations(input_string):
    matches = df[df['NAME'].str.contains(input_string)]
    match = matches[:1]
    lat2 = match.iloc[0]['Laenge']
    lon2 = match.iloc[0]['Breite']
    df_distance = df
    df_distance['Distance'] = df.apply(lambda row: haversine(row['Laenge'], row['Breite'], lat2, lon2), axis=1)
    df_distance = df_distance.query('Distance <= 8')
    df_distance = df_distance[:8]
    stations_list = []
    for index, row in df_distance.iterrows():
        stations_list.append(([row['NAME'], row['station_id']]))
    return stations_list


session = get_tor_session()
url = 'https://reiseauskunft.bahn.de/bin/query.exe/dn?ld=4314&country=DEU&protocol=https:&rt=1&OK='
df = pd.read_parquet('D_Bahnhof_2020_alle.parquet')
date = input('On what day do you want to travel?\n')
start_stations = find_stations(input('Start station:\n'))
print(start_stations)
end_stations = find_stations(input('Arrival station:\n'))
print(end_stations)
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
start(start_stations, end_stations, date)
