"""
  FileName     [ transportation.py ]
  PackageName  [ statistics ]
  Synopsis     [ Basic unit of bus routes class ]
"""

from collections.abc import Iterable
import itertools
import pandas as pd
import numpy as np

class BusRouteManager():
    def __init__(self, dfs):
        self.dfs = dfs

        self.routes = dfs['routes']
        self.stop_code = dfs['stop_code']

        for key in ('stop_code', 'routes'):
            if key in self.dfs:
                del self.dfs[key]

    def routes_available(self):
        return sorted(set([ key[:key.index('-')] for key in self.dfs.keys() ]))

    def routes_directions_available(self):
        return sorted(set([ (key[:key.index('-')], key[key.index('-') + 1:]) for key in self.dfs.keys() ]))

    def exists(self, route) -> bool:
        """ 
        Return True if the route data is exists 
        """
        return True if route in self.routes_available() else False

    def direction(self, route) -> tuple:
        return tuple(self.getRoute(route, None).keys())
        # return self.routes.set_index('routeName').loc[route, ['Latitude', 'Longitude']].to_dict()

    def getRoute(self, route, direction=None):
        """ 
        Return the routeStop information of the route 
        """
        if direction is None:
            return { key[key.index('-') + 1:] : self.dfs[key] for key in self.dfs.keys() if route == key[:key.index('-')] }

        for key in self.dfs.keys():
            r = key[:key.index('-')]
            d = key[key.index('-') + 1:]

            if route == r and direction == d:
                return self.dfs[key]

    def getRouteStops(self, route, direction=None, mode='alias') -> list:
        """ 
        Return the station which the *route* passby. 
        """
        stops = []

        if mode == 'alias':
            column = 'staName'

        if mode == 'code':
            column = 'staCode'

        for key in self.dfs.keys():
            if route == key[:key.index('-')]:
                stops.extend(self.dfs[key][column].tolist())

        return stops

    def available_to_go(self, route, direction, stop1, stop2, mode='staName'):
        """ 
        Return True if it's available to go to *stop2* by *stop1* by the bus *route* 
        """
        stops = self.getRoute(route, direction)

        index1, index2 = None, None

        if stop1 in stops[mode].unique():
            index1 = stops[mode][ stops[mode] == stop1 ].index.values
        
        if stop2 in stops[mode].unique():
            index2 = stops[mode][ stops[mode] == stop2 ].index.values

        # Return False if any station name can't be search
        if (index1 is None) or (index2 is None):
            return False

        for origin, destination in itertools.product(index1, index2):
            if destination - origin > 0:
                return True

        # Return True only if station1 can arrive to station2
        return False
        
    def is_terminal(self, stop, mode='staName'):
        """ 
        Return True if it's a terminal station for some routes 
        """
        mode = 0 if mode == 'staCode' else 1

        for route, direction in self.routes_directions_available():
            if stop in self.getRoute(route, direction).iloc[[0, -1], 1].unique():
                return True

        return False

    def route_in_stop(self, station, mode='staName'):
        """ 
        Return list of routes that can arrive *station* 
        """
        routes = []

        for route, direction in self.routes_directions_available():
            if station in self.getRoute(route, direction)[mode].unique():
                routes.append((route, direction))

        return routes

    def route_available_in_stop(self, stop, mode='staName'):
        """ 
        Return list of routes that is available to lend on at *station*. 
        """
        routes = []
        for route, direction in self.routes_directions_available():
            if stop in self.getRoute(route, direction)[mode][:-1].unique():
                routes.append((route, direction))

        return routes

    def station_passby(self, route, stop1, stop2, mode='staName') -> list:
        """ 
        Return the bus stations name list 

        Parameters
        ----------
        route :
            ...
        stop1, stop2 :
            ...
        mode : 
            ...

        Return
        ------
        list :
            ...
        """        
        directions = self.direction(route)

        for d in directions:
            stops = self.getRoute(route, d)

            if self.available_to_go(route, d, stop1, stop2):       
                index1 = stops[mode][ stops[mode] == stop1 ].index.values
                index2 = stops[mode][ stops[mode] == stop2 ].index.values

                # Minimum path searching algorithm
                result = 0
                buffer = []

                for origin, destination in itertools.product(index1, index2):
                    if destination - origin > result:
                        result = destination - origin
                        buffer.append((origin, destination))

                index1, index2 = buffer.pop()
                return stops.loc[index1: index2, mode].to_list()

        return []

    def inference_interchange_station(self, route1, stop1, route2, stop2):
        """ 
        Inference the bus-stop name by the first and second route, origin and destination point
        
        Parameters
        ---------
        route1, stop1, route2, stop2 : str
        
        Return
        ---------
        interchange_station : str
            ....
        """
        raise NotImplementedError

    def station_coordinates(self, station=None, mode='staName') -> dict:
        """ 
        Return the coordinates of station 
        
        Parameters
        ----------
        stations : {str, None} optional
            ....
        """
        if station is None:
            mapping = self.stop_code.set_index(mode).to_dict()
            return mapping

        mapping = self.stop_code[[mode, 'Latitude', 'Longitude']].set_index(mode).loc[station].mean().to_dict()

        return mapping

    def stations_nearby(self, stations, meters=None, kilometers=None) -> list:
        """ 
        Return the list of stations nearby.
        
        Parameters
        ----------
        station : str
            ....

        meters, kilometers : float
            ....

        Return
        ------
        stations : list
            ....
        """
        return

    def route_station_distance(self, route, direction) -> np.ndarray:
        raise NotImplementedError

class LRTManager():
    def __init__(self):
        raise NotImplementedError

def update_coordinate():
    dfs = pd.read_excel("./src/stop_code.xlsx", sheet_name=None, header=0, index_col=None)
    coordinates = dfs['stop_code'].set_index('staCode')
    latitude = coordinates['Latitude'].to_dict()
    longtitude = coordinates['Longtitude'].to_dict()
    
    del dfs['stop_code']
    del dfs['routes']
    dfs = [df for df in dfs.values()]

    stops = pd.concat(dfs, ignore_index=True).drop_duplicates().sort_values(by=['staCode']).reset_index(drop=True)
    stops.columns = ['staCode', 'staName']
    stops['Latitude'] = stops['staCode'].map(latitude)
    stops['Longtitude'] = stops['staCode'].map(longtitude)

    mask = stops['Latitude'].isna()
    coordinates = coordinates.reset_index().set_index('staName')
    latitude = coordinates['Latitude'].to_dict()
    longtitude = coordinates['Longtitude'].to_dict()
    stops['Latitude'][mask] = stops['staName'][mask].map(latitude)
    stops['Longtitude'][mask] = stops['staName'][mask].map(longtitude)

    stops = stops.values.tolist()
    stops = sorted(stops, key=lambda x: int(x[0][1:].split('/')[0]))

    stops = pd.DataFrame(stops, columns=['staCode', 'staName', 'Latitude', 'Longtitude'])
    stops.to_excel("./src/stop_code_modify.xlsx", index=False)

def getRouteAndCompanyList():
    return res('https://bis.dsat.gov.mo:37812/macauweb/getRouteAndCompanyList.html', {'lang': 'zh-tw'})

def getRouteStation(route: str, direction: str):
    url = 'https://bis.dsat.gov.mo:37812/macauweb/getRouteData.html'
    data = {'action': 'sd', 'routeName': route, 'dir': direction, 'lang': 'zh-tw'}
    return res(url, data)

def res(url, data):
    import requests

    response = requests.post(url=url, data=data).text
    return response

def update_stations(args):
    routes = json.loads(getRouteAndCompanyList())

    flags = {}
    for bus in routes['data']['companyList']:
        color, company = bus.items()
        flags[color[1]] = company[1]

    routes = pd.DataFrame(routes['data']['routeList'])
    routes['color'] = routes['color'].map(flags)
    routes.columns = ['Company', 'RouteName']

    responses = {}
    
    crawl_list = list(itertools.product(routes.RouteName, range(0, 2)))
    for index, (name, direction) in enumerate(crawl_list, 1):
        print('[{:>3d} / {:>3d}]'.format(index, len(crawl_list)))

        response = json.loads(getRouteStation(name, direction))['data']
        
        if 'error' in response: 
            continue
            
        df = pd.DataFrame(response['routeInfo'])[['staCode', 'staName']]

        if name not in responses:
            responses[name] = {}
        
        responses[name][direction] = df

    with pd.ExcelWriter(args.output) as writer:
        routes.to_excel(writer, sheet_name='Routes', index=False)

        for key, values in responses.items():
            if len(values) == 1:
                direction = '循環線'
                df = values[0]
                df.to_excel(writer, sheet_name='{}({})'.format(key, direction).replace('/', ''), index=False)

            if len(values) == 2:
                for direction, value in values.items():
                    direction = '往{}'.format(value.iloc[-1, 1])
                    df = value
                    df.to_excel(writer, sheet_name='{}({})'.format(key, direction).replace('/', ''), index=False)

    return
    
def main():
    dfs = pd.read_excel('./src/stop_code.xlsx', sheet_name=None, index_col=None, header=0)
    routes = BusRouteManager(dfs)

    # Unittest 1
    test_data = [
        ('33', 'Forward', '筷子基總站', '南新花園', True),
        ('33', 'Forward', '南新花園', '筷子基總站', True),
        ('25', 'Forward', '關閘總站', '水坑尾/公共行政大樓', True),
        ('25', 'Forward', '關閘總站', '水坑尾', False)
    ]

    for index, (route, direction, stop1, stop2, ans) in enumerate(test_data, 1):
        result = (ans == routes.available_to_go(route, direction, stop1, stop2))

        if result == True:
            print("Case", index, ": passed")

        if result == False:
            print(index, route, direction, stop1, stop2)
    
    # Unittest 2
    test_data = [
        ('筷子基總站', True), ('關閘總站', True), ('新口岸/科英布拉街', True),
    ]

    for index, (stop, ans) in enumerate(test_data, 1):
        result = (ans == routes.is_terminal(stop))

        if result == True:
            print("Case", index, ": passed")

        if result == False:
            print(index, stop)

    # Unittest 3
    test_data = ['亞馬喇前地', '筷子基總站']

    for station in test_data:
        print(routes.station_coordinates(station))

    print(routes.station_coordinates())

    return

if __name__ == '__main__':
    main()
