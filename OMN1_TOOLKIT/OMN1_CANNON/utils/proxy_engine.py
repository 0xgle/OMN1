def load_proxies(filename):
    try:
        with open(filename) as f:
            return [line.strip() for line in f if line.strip()]
    except:
        return []

def rotate_proxy(proxies):
    import random
    return random.choice(proxies) if proxies else None
