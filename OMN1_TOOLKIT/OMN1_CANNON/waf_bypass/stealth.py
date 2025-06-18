import random

def generate_stealth_headers():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.3 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ]
    languages = ["en-US,en;q=0.9", "pl-PL,pl;q=0.9", "fr-FR,fr;q=0.8"]
    referers = ["https://www.google.com/", "https://www.bing.com/", "https://duckduckgo.com/"]

    headers = {
        "User-Agent": random.choice(user_agents),
        "Accept-Language": random.choice(languages),
        "Referer": random.choice(referers),
        "X-Forwarded-For": ".".join(str(random.randint(1, 255)) for _ in range(4)),
        "Origin": "https://www.google.com",
    }

    return headers