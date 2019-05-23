import os
import pandas as pd
import numpy as np
import requests
import bs4 as bs
import time
import re

http_proxy  = "http://165.225.104.34:9480"
https_proxy = "https://165.225.104.34:9480"
proxyDict = { "http"  : http_proxy, "https" : https_proxy }

baseUrl = "https://results.eci.gov.in/pc/en/trends/"
def_url = "https://results.eci.gov.in/pc/en/trends/statewise{0}.htm?st={0}"
states = {
"S011" : "Andhra Pradesh"," S021" : "Arunachal Pradesh"," S031" : "Assam"," S041" : "Bihar"," S261" : "Chhattisgarh"," S051" : "Goa"," S061" : "Gujarat"," S071" : "Haryana"," S081" : "Himachal Pradesh"," S091" : "Jammu & Kashmir"," S271" : "Jharkhand"," S101" : "Karnataka"," S111" : "Kerala"," S121" : "Madhya Pradesh"," S131" : "Maharashtra"," S141" : "Manipur"," S151" : "Meghalaya"," S161" : "Mizoram"," S171" : "Nagaland"," S181" : "Odisha"," S191" : "Punjab"," S201" : "Rajasthan"," S211" : "Sikkim"," S221" : "Tamil Nadu"," S291" : "Telangana"," S231" : "Tripura"," S241" : "Uttar Pradesh"," S281" : "Uttarakhand"," S251" : "West Bengal", "U011" : "Andaman & Nicobar Islands", "U021" : "Chandigarh", "U031" : "Dadra & Nagar Haveli", "U041" : "Daman & Diu", "U061" : "Lakshadweep", "U051" : "NCT OF Delhi", "U071" : "Puducherry"}
cols = ["State/UT", "Constituency", "Leading_Candidate", "Leading_Party", "Trailing_Candidate", "Trailing_Party", "Margin", "Status" ]
fulDf = pd.DataFrame(columns=cols)
nextUrls = []

def fetchData(url):
    t1 = time.time()
    r = requests.get(url, proxies=proxyDict)
    soup = bs.BeautifulSoup(r.content,'lxml')
    df = pd.DataFrame(columns=cols)
    try:
        table = soup.find_all('table', attrs={'width':'100%'})[4]
        table_rows = table.find_all('tr', attrs={'style':"font-size:12px;"})
        for j, tr in enumerate(table_rows):
            if loadNextUrls:
                refs = table.find_all('a')
                if len(refs) > 2:
                    for k in range(2, len(refs)):
                        ref = refs[k]
                        result = re.findall('"([^"]*)"', str(ref))
                        if '#' not in result[0] and 'nxt' not in result[0] :
                            nextUrls.append(baseUrl+result[0])
            tds = tr.find_all('td')
            df = pd.DataFrame([[states[p], tds[0].text, tds[2].text, tds[4].text, \
                              tds[12].text, tds[14].text, tds[24].text, tds[25].text]], columns = cols)
    except requests.exceptions.ConnectionError:
        print "Connection timeout for ", url
    t2 = time.time()
    return df

def runAll()
    for i, p in enumerate(states):
        url = def_url.format(p)
        url = url.replace(' ', '')
        print url
        fulDf.append(fetchData(url))

    for url in nextUrls:
        url = baseUrl + url
        print url
        fulDf.append(fetchData(url))
    
  
if __name__ == '__main__':
    runAll()
    