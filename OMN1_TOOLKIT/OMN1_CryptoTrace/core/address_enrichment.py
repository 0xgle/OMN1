# ========================
# MODUŁ: core/address_enrichment.py
# ========================

# Uzupełnianie informacji o adresie ETH/BTC z OSINT źródeł – np. chainabuse, scamdb, darknet

import requests

def enrich_eth_address_chainabuse(address):
    url = f"https://api.chainabuse.com/api/v1/reports/address/{address}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and data:
                return True, f"Zgłoszenia: {len(data)} (ChainAbuse)"
        return False, "Brak zgłoszeń (ChainAbuse)"
    except:
        return False, "[Błąd] Brak dostępu do ChainAbuse API"

def enrich_eth_address_etherscan_label(address, api_key):
    url = f"https://api.etherscan.io/api?module=account&action=getcontractcreation&address={address}&apikey={api_key}"
    try:
        response = requests.get(url).json()
        creator = response.get('result', {}).get('contractCreator')
        if creator:
            return True, f"Stworzony przez: {creator[:10]}..."
        else:
            return False, "Brak informacji o kontrakcie."
    except:
        return False, "[Błąd] Brak odpowiedzi od Etherscan."

def enrich_summary(address, network='ethereum', api_key=None):
    print(f"\n📡 Wzbogacanie informacji o adresie: {address}")

    found, info = enrich_eth_address_chainabuse(address)
    print(f"🔎 ChainAbuse: {info}")

    if network == 'ethereum' and api_key:
        found2, info2 = enrich_eth_address_etherscan_label(address, api_key)
        print(f"🔎 Etherscan Label: {info2}")
