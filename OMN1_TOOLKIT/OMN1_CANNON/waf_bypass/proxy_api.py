import requests
import random

def fetch_proxy_list():
    url = "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=5000&country=all&ssl=all&anonymity=all"
    try:
        response = requests.get(url, timeout=10)
        proxy_list = response.text.strip().split('\n')
        return [proxy.strip() for proxy in proxy_list if proxy.strip()]
    except Exception as e:
        print(f"[!] Failed to fetch proxy list: {e}")
        return []

def get_random_proxy(proxy_list):
    return random.choice(proxy_list) if proxy_list else None