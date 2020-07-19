"""
  FileName      [ opendataset.py ]
  PackageName   [ macau-data ]
  Synopsis      [ ]
  Author        [ EdwardLeeMacau ]
  Reference     [  ]
"""

import json
import xml.etree.ElementTree as ET

import requests
from bs4 import BeautifulSoup


def getAPIdir(url) -> dict:
    return {}

def getRestaurantInfo() -> list:
    """
    Return
    ------
    header : list
        The attribute of each restaurants

    contents : list
        The information of all restaurants with the attribute **header**
    """

    res = requests.get(url="https://dst.apigateway.data.gov.mo/dst_restaurant", 
        headers={'Authorization': 'APPCODE 09d43a591fba407fb862412970667de4'})
    res.encoding = "utf-8" 

    root = ET.fromstring(res.text)
    header = list(map(lambda x: x.tag, root.find('restaurant')))
    contents = [list(map(lambda x: x.text, restaurant)) for restaurant in root.findall('restaurant')]

    return header, contents

def getParkingLotInfo() -> list:
    """
    Return
    ------
    header : list
        The attribute of each parking-lots

    contents : list
        The information of all parking-lots with the attribute **header**
    """
    res = requests.get(url="https://dsat.apigateway.data.gov.mo/car_park_detail", 
        headers={'Authorization': 'APPCODE 09d43a591fba407fb862412970667de4'})
    res.encoding = "utf-8" 

    root = ET.fromstring(res.text)
    header = list(map(lambda x: x.attrib, root.find('Car_park_info')))
    contents = [park.attrib for park in root.findall('Car_park_info')]

    return header, contents

def getParkingLotRealTimeInfo() -> list:
    """
    Return
    ------
    header : list
        The attribute of each parking-lots

    contents : list
        The information of all parking-lots with the attribute **header**
    """
    res = requests.get(url="https://dsat.apigateway.data.gov.mo/car_park_maintance", 
        headers={'Authorization': 'APPCODE 09d43a591fba407fb862412970667de4'})
    res.encoding = "utf-8" 

    root = ET.fromstring(res.text)
    header = list(map(lambda x: x.attrib, root.find('Car_park_info')))
    contents = [park.attrib for park in root.findall('Car_park_info')]

    return header, contents

def getBusRouteInfo():
    """
    Return
    ------
    header : list
    
    contents : list
    """
    res = requests.get(url="https://api.data.gov.mo/datadir/downloadSingleFile?fileId=722&dataDirId=e7b2e84d-3333-42f0-b676-64ce95306f0d&token=xh4EOsR3lJ87QsC7ly8CzqTGeHHedY1J")

    with open('collect-data/bus.zip', 'wb') as file:
        file.write(res.content)

def main():
    getParkingLotRealTimeInfo()
    return

if __name__ == "__main__":
    main()
