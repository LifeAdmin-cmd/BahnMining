import sys
import time

from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import requests


def getHtml(data, day_count):
    retry_count = 0
    max_retries = 5

    while retry_count < max_retries:
        try:
            date = (datetime.now() + timedelta(days=day_count)).strftime('%d.%m.%Y')
            print(date, day_count)
            data = data.format(date)
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


def getPrices(prices_html):
    temp_prices = []
    for price in prices_html:
        price = price.text.strip()
        price = price.split("\n")[1].strip()  # Remove the unwanted text
        price = price.replace("\xa0€", "").strip()  # Remove the whitespace and currency symbol
        price = float(price.replace(",", "."))  # Replace the comma with a dot for floating-point numbers
        temp_prices.append(price)
    print(temp_prices)
    return temp_prices


def saveData(final_prices):
    pricesArray.append(final_prices)


def start():
    for days in range(1, 11):
        retry_count = 0
        max_retries = 10
        while retry_count < max_retries:
            html_text = getHtml(dataArray[0], days)
            soup = BeautifulSoup(html_text, 'lxml')
            # from_field = soup.find_all('div', id='tbpSlotContainer')
            prices_html = soup.find_all('div', class_='tbpSlotPrice')
            html_prices = getPrices(prices_html)
            if html_prices:
                saveData(html_prices)
                break
            retry_count += 1
            print('Data missing. {}/{} retries'.format(retry_count, max_retries))
            time.sleep(2.5)
            if retry_count == max_retries:
                sys.exit('Too many retries. Exiting program.')
        # print('Job failed')
        # break


url = 'https://reiseauskunft.bahn.de/bin/query.exe/dn?ld=4314&country=DEU&protocol=https:&rt=1&OK='
dataArray = [
    'HWAI%3DQUERY%21rit=no&queryPageDisplayed=yes&HWAI%3DQUERY%21displayed=yes&HWAI%3DJS%21ajax=yes&HWAI%3DJS%21js' \
    '=yes&REQ0JourneyStopsS0A=255&REQ0JourneyStopsS0G=Porz%28Rhein%29&REQ0JourneyStopsS0ID=A%3D1%40O%3DPorz%28Rhein' \
    '%29%40X%3D7064721%40Y%3D50882910%40U%3D80%40L%3D008004869%40B%3D1%40p%3D1675279635%40' \
    '&REQ0JourneyStopsS0a=131072&REQ0JourneyStopsZ0A=255&REQ0JourneyStopsZ0G=Middelburg' \
    '&REQ0JourneyDate={}&REQ0JourneyTime=14%3A00' \
    '&REQ0HafasSearchForw=1&REQ1JourneyDate=&REQ1JourneyTime=&REQ1HafasSearchForw=1&useFastConnectionsOnly=on&HWAI' \
    '%3DQUERY%24PRODUCTS%240_0%21show=yes&traveller_Nr=1&REQ0Tariff_TravellerType.1=Y' \
    '&REQ0Tariff_TravellerReductionClass.1=0&REQ0Tariff_TravellerAge.1=&REQ0Tariff_Class=2&REQ0HafasChangeTime=0' \
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
pricesArray = []
start()
print(pricesArray)
print("Bytes: " + str(sys.getsizeof(pricesArray)))

