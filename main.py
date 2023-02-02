from bs4 import BeautifulSoup
import requests


def getHtml(data):
    data = data.format('05.02.23')
    request = requests.post(url, data=data)
    print(request)
    return request.text


def getPrices(prices_html):
    prices = []
    for price in prices_html:
        price = price.text.strip()
        price = price.split("\n")[1].strip()  # Remove the unwanted text
        price = price.replace("\xa0€", "").strip()  # Remove the whitespace and currency symbol
        price = float(price.replace(",", "."))  # Replace the comma with a dot for floating-point numbers
        prices.append(price)
    return prices


url = 'https://reiseauskunft.bahn.de/bin/query.exe/dn?ld=4314&country=DEU&protocol=https:&rt=1&OK='
dataArray = [
    'HWAI%3DQUERY%21rit=no&queryPageDisplayed=yes&HWAI%3DQUERY%21displayed=yes&HWAI%3DJS%21ajax=yes&HWAI%3DJS%21js' \
       '=yes&REQ0JourneyStopsS0A=255&REQ0JourneyStopsS0G=K%F6ln+Hbf&REQ0JourneyStopsS0ID=A%3D1%40O%3DK%F6ln+Hbf%40X' \
       '%3D6958730%40Y%3D50943029%40U%3D80%40L%3D8000207%40B%3D1%40p%3D1675107033%40&REQ0JourneyStopsS0o=8' \
       '&REQ0JourneyStopsS0a=131072&REQ0JourneyStopsZ0A=255&REQ0JourneyStopsZ0G=Middelburg&REQ0JourneyStopsZ0ID=A%3D1' \
       '%40O%3DMiddelburg%40X%3D3617080%40Y%3D51494832%40U%3D80%40L%3D008400436%40B%3D1%40p%3D1675107033%40' \
       '&REQ0JourneyStopsZ0o=8&REQ0JourneyStopsZ0a=131072&REQ0JourneyDate={}&REQ0JourneyTime=14%3A00' \
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
htmlText = getHtml(dataArray[0])
soup = BeautifulSoup(htmlText, 'lxml')
fromField = soup.find_all('div', id='tbpSlotContainer')
pricesHtml = soup.find_all('div', class_='tbpSlotPrice')
print(getPrices(pricesHtml))
