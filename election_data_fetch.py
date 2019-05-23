import os
import pandas as pd
import numpy as np
import requests
import bs4 as bs
import time
import re

http_proxy   = '' # Edit if you are behind corporate proxy  schema 'username@password:http://url:port'
https_proxy  = '' # Edit if you are behind corporate proxy  schema 'username@password:https://url:port'
proxyDict = { "http"  : http_proxy, "https" : https_proxy }

baseUrl = "https://results.eci.gov.in/pc/en/trends/"
def_url = "https://results.eci.gov.in/pc/en/trends/statewise{0}.htm?st={0}"
states = {
"S011": "Andhra Pradesh","S021": "Arunachal Pradesh","S031": "Assam","S041": "Bihar","S261": \
    "Chhattisgarh","S051": "Goa","S061": "Gujarat","S071": "Haryana","S081": "Himachal Pradesh",\
    "S091": "Jammu & Kashmir","S271": "Jharkhand","S101": "Karnataka","S111": "Kerala","S121": \
    "Madhya Pradesh","S131": "Maharashtra","S141": "Manipur","S151": "Meghalaya","S161": \
    "Mizoram","S171": "Nagaland","S181": "Odisha","S191": "Punjab","S201": "Rajasthan",\
    "S211": "Sikkim","S221": "Tamil Nadu","S291": "Telangana","S231": "Tripura",\
    "S241": "Uttar Pradesh","S281": "Uttarakhand","S251": "West Bengal", \
    "U011": "Andaman & Nicobar Islands", "U021": "Chandigarh", "U031": "Dadra & Nagar Haveli", \
    "U041": "Daman & Diu", "U061": "Lakshadweep", "U051": "NCT OF Delhi", "U071": "Puducherry"}

cols = ["State/UT", "Constituency", "Leading_Candidate", "Leading_Party", "Trailing_Candidate", "Trailing_Party", "Margin", "Status" ]
nextUrls = []

def fetchData(st, url, checkNextUrls):
    soup = None
    res = False
    df = pd.DataFrame(columns=cols)
    try:
        r = requests.get(url, proxies=proxyDict)
        soup = bs.BeautifulSoup(r.content,'lxml')
    except requests.exceptions.ConnectionError:
        print ("Connection timeout for ", url)
    
    if soup:
        table = soup.find_all('table', attrs={'width':'100%'})[4]
        table_rows = table.find_all('tr', attrs={'style':"font-size:12px;"})
        for j, tr in enumerate(table_rows):
            refs = table.find_all('a')
            # for states where results are rendered in multiple html pages
            if checkNextUrls and len(refs) > 2:
                for k in range(2, len(refs)):
                    ref = refs[k]
                    result = re.findall('"([^"]*)"', str(ref))
                    if '#' not in result[0] and 'nxt' not in result[0] :
                        nextUrls.append((st, baseUrl+result[0]))
            tds = tr.find_all('td')
            df = df.append(pd.DataFrame([[st, tds[0].text, tds[2].text, tds[4].text, \
                              tds[12].text, tds[14].text, tds[24].text, tds[25].text]], columns = cols))
            res = True
    return df, res

def runAll():
    checkNextUrls = True
    fulDf = pd.DataFrame(columns=cols)
    for i, p in enumerate(states):
        url = def_url.format(p)
        url = url.replace(' ', '')
        print (url)
        df, res = fetchData(states[p], url, checkNextUrls)
        if not res:
            nextUrls.append((st, url, checkNextUrls))
        else:
            fulDf = fulDf.append(df)        

    for url in set(nextUrls):
        st = url[0]
        url = url[1]
        checkNextUrls=False
        if len(url) > 2:
            checkNextUrls=True
        print (url)
        df, res = fetchData(states[p], url, checkNextUrls)
        if not res:
            nextUrls.append((st, url, checkNextUrls))
        else:
            fulDf = fulDf.append(df)
        break        
    return fulDf
    
if __name__ == '__main__':
    fulDf = runAll()
    fulDf.to_csv('result_data.csv')
    
