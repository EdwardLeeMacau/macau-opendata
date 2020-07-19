"""
  FileName      [ dsej.py ]
  PacakageName  [ macau-data ]
  Synopsis      [  ]
  Author        [ EdwardLeeMacau ]
  Reference     [  ]
"""

import json
import os
import time

import pandas as pd
import requests
from bs4 import BeautifulSoup

# import selenium

DSAT_STUDENT_API = 'http://appl.dsej.gov.mo/eduenquiry/edu/eduweb/schinf/schstat.jsp?stat_date=2018-10-26&s_code={}&lang=c'

def crawl(url):
    soup = BeautifulSoup(requests.post(url=url).text)

    table = soup.find('table')

    df = pd.DataFrame()    
    column = [ td.text.strip() for td in table.find('tr').find_all('td') ]

    for index, tr in enumerate(table.find_all('tr')):
        # Table Header
        if index == 0: 
            continue

        # Table content
        row = [ td.text.strip() for td in tr.find_all('td') ]
        df = df.append([row])

    if not df.empty:
        # Set format
        df = df.set_index(keys=0)
        df.columns = column[1:]
        df.index.name = column[0]

        return df

def main():
    dfs = {}

    for s_code in range(1, 201):
        url = DSAT_STUDENT_API.format(str(s_code).zfill(3))
        df = crawl(url)
        
        if df is not None:
            dfs[s_code] = df
            
    with pd.ExcelWriter('student_stat.xlsx') as writer:
        for s_code, df in dfs.items():
            df.to_excel(writer, sheet_name=str(s_code).zfill(3))

    return

if __name__ == "__main__":
    main()
