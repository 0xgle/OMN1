
import requests
import random

def fetch_live_proxies():
    """
    Fetch live HTTP proxies from a public API.
    You can replace the URL with a premium provider for more stability.
    """
    try:
        url = "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=1000&country=all"
        response = requests.get(url, timeout=10)
        proxies = response.text.strip().split('\n')
        return [p for p in proxies if p.strip()]
    except Exception as e:
        print(f"[!] Failed to fetch proxies: {e}")
        return []

def get_random_proxy():
    proxy_list = fetch_live_proxies()
    if proxy_list:
        chosen = random.choice(proxy_list)
        print(f"[i] Using proxy: {chosen}")
        return {
            "http://": f"http://{chosen}",
            "https://": f"http://{chosen}",
        }
    print("[!] No proxy available, proceeding without proxy.")
    return None
