"""
  FileName      [ dsat.py ]
  PackageName   [ macau-data ]
  Synopsis      [  ]
  Author        [ EdwardLeeMacau ]
  Reference     [  ]
"""

import argparse
import json
import os
import time

import pandas as pd
import requests

def requestHeader():
    return

def getRouteAndCompanyList() -> pd.DataFrame:
    """ 
    Return the available routes. 

    Return
    ------
    routes : pd.DataFrame
        ...
    """

    url = 'https://bis.dsat.gov.mo:37812/macauweb/getRouteAndCompanyList.html'
    response = json.loads(requests.post(url=url).text)
    response, header = response['data'], response['header']

    # Map the color to the company name
    company = { c['color']: c['name'] for c in response['companyList'] }
    routes = pd.DataFrame(response['routeList'])
    routes['Company'] = routes['color'].map(company)

    # Remove the column *color*
    routes = routes[['routeName', 'Company']]

    # Rename the columns
    routes.columns = ['RouteName', 'Company']

    return routes

def getAllZone() -> dict:
    """ Get the shape of each zone. """
    url = 'https://bis.dsat.gov.mo:37016/app/traffic-status/api/proxy/traffic/zone/getAllZone'
    response = json.loads(requests.get(url=url).text)

    return response['data']

def getAllZoneRtStatus() -> pd.DataFrame:
    """ Return the status of each zone with the attribute *effIndex* and *statTime* """
    url = 'https://bis.dsat.gov.mo:37016/app/traffic-status/api/proxy/traffic/zone/getAllZoneRtStatus?tp=&zoneType=&opType='
    response = json.loads(requests.get(url=url).text)

    zoneRtStatus = pd.DataFrame(response['data'])

    return zoneRtStatus

def getAllLink():
    """ Return the status of each link. """
    url = 'https://bis.dsat.gov.mo:37016/app/traffic-status/api/proxy/traffic/link/getAllLink'
    response = json.loads(requests.get(url=url).text)

    links = pd.DataFrame(response['data'])

    return links

def getRouteLineCoor():
    """ Return the coordinates of the buses and stations. """ 
    url = "https://bis.dsat.gov.mo:37812/macauweb/getRouteLineCoor.html"
    response = json.loads(requests.post(url=url).text)
    
    return response['data']

def getRoutesInformation(routes, save=None):
    """ 
    Return the name of bus stops for the specified route 
    
    Parameters
    ----------
    routes : pd.DataFrame
        The routes ready to retrieve

    Return
    ------
    dfs : pandas.dataframe
        ....
    """
    routes = routes.set_index('RouteName')
    routes['Forward'] = None
    routes['Backward'] = None
    dfs = {}

    url = 'https://bis.dsat.gov.mo:37812/macauweb/getRouteData.html'
    
    for route in routes.index.tolist():
        for idx, direction in enumerate(['Forward', 'Backward']):
            # Make request
            data = {'action': 'sd', 'routeName': route, 'dir': str(idx), 'lang': 'zh-tw'}
            response = json.loads(requests.post(url=url, data=data).text)
            response, header = response['data'], response['header']

            print(header)

            # If get nothing, skip this one
            if 'error' in response:
                continue

            # Route Information
            df = pd.DataFrame(response['routeInfo'])
            dfs['{}-{}'.format(route, direction)] = df[['staCode', 'staName']]

            # Summary Table
            routes.at[route, direction] = df.tail(1)['staName'].values[0]

    # Fill Summary Table
    routes['Backward'][ routes['Backward'].isna() ] = routes['Forward'][ routes['Backward'].isna() ]
    routes = routes.reset_index()
    
    # New subtable
    dfs['stop_code'] = pd.concat(dfs.values(), axis=0).drop_duplicates().sort_values('staCode').reset_index(drop=True)

    # New subtable
    dfs['routes'] = routes

    if save is not None:
        dfs['stop_code']['sort_key'] = dfs['stop_code']['staCode'].str[1:].str.split('/').str.get(0).astype(int)
        dfs['stop_code'] = dfs['stop_code'].sort_values('sort_key').reset_index(drop=True)

        with pd.ExcelWriter(save) as writer:
            for df in dfs:
                dfs[df].to_excel(writer, sheet_name=df, index=False)


    return dfs

def res(route: str, direction: str, root: str):
    """ Request DSAT server to get the bus location. """

    while True:
        _time = time.strftime("%d/%m/%Y %H:%M:%S", time.localtime())
        url = 'https://bis.dsat.gov.mo:37812/macauweb/getRouteData.html'
        data = {'action': 'dy', 'routeName': route, 'dir': direction, 'lang': 'zh-tw'}

        resposne = requests.post(url=url, data=data).text

        with open(os.path.join(root, "{}-{}.txt".format(route, direction)), 'a') as file:
            file.write('[{}]\n{}\n\n'.format(_time, resposne))

        print("Route: {:>4s}, Direction: {:>4s}, Time: {}".format(route, direction, _time))
        time.sleep(30)

    return

def main():
    routes = getRouteAndCompanyList()

    # print(getAllZone())
    # print(getAllZoneRtStatus())
    # print(getAllLink())
    # print(getRouteLineCoor())
    
    # dfs = getRoutesInformation(routes, save='collect-data/bus-route.xlsx')

    return

if __name__ == "__main__":
    main()
