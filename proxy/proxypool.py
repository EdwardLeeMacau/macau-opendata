"""
  FileName      [ proxypool.py ]
  PacakageName  [ proxy ]
  Synopsis      [  ]
  Author        [ EdwardLeeMacau ]
  Reference     [  ]
"""

import json
import pprint

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


def proxy_check_available(proxy) -> bool:
    try:
        ip = requests.get('https://httpbin.org/ip', proxies=proxy, timeout=1).json()['origin']
        return True
    except requests.ReadTimeout:
        print('/')
    except requests.ConnectTimeout:
        print('/')
    except requests.ConnectionError:
        print('/')

    return False

def getProxyPools():
    """ TODO: US-Proxy provides a API to retrieve the proxy list """
    proxypools = []
    start_urls = 'https://www.us-proxy.org'
    response = requests.get(start_urls)

    soup = BeautifulSoup(response.text, 'lxml')

    for tr in soup.select('#proxylisttable tr'):
        tds = tr.select('td')

        if len(tds) == 8:
            ip = tds[0].text
            port = tds[1].text
            anonymity = tds[4].text
            scheme = 'https' if tds[6].text == 'yes' else 'http'
            proxy = '{:s}://{:s}:{:s}'.format(scheme, ip, port)                

            if proxy_check_available({scheme: proxy}):
                proxypools.append({"scheme": scheme, "proxy": proxy, "port": port})

    return proxypools

def main():
    with open('./proxy-pools.json', 'w') as jsonfile:
        jsonfile.write(json.dumps(getProxyPools()))

    return

if __name__ == "__main__":
    main()
