import requests

def get_eth_transactions(address, api_key, direction="in", limit=10):
    """
    Pobiera transakcje Ethereum (IN/OUT) z Etherscan API.

    :param address: Adres ETH
    :param api_key: Klucz API Etherscan
    :param direction: 'in' | 'out'
    :param limit: Maksymalna liczba transakcji
    :return: Lista transakcji
    """
    url = (
        f"https://api.etherscan.io/api"
        f"?module=account&action=txlist"
        f"&address={address}"
        f"&startblock=0&endblock=99999999"
        f"&sort=desc"
        f"&apikey={api_key}"
    )

    try:
        response = requests.get(url)
        data = response.json()
        txs = data.get("result", [])

        filtered = []
        for tx in txs:
            from_addr = tx["from"].lower()
            to_addr = tx["to"].lower()
            addr = address.lower()

            # filtrowanie IN lub OUT
            if direction == "in" and to_addr == addr:
                filtered.append({
                    "from": from_addr,
                    "to": to_addr,
                    "value": round(int(tx["value"]) / 1e18, 8)
                })
            elif direction == "out" and from_addr == addr:
                filtered.append({
                    "from": from_addr,
                    "to": to_addr,
                    "value": round(int(tx["value"]) / 1e18, 8)
                })

        print(f"[DEBUG] {direction.upper()} transakcji znaleziono: {len(filtered)}")
        return filtered[:limit]

    except Exception as e:
        print(f"[BŁĄD] Błąd przy pobieraniu transakcji: {e}")
        return []
