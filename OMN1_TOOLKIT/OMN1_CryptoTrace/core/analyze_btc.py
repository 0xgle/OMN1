import requests
import csv
import os

def analyze_btc_address(address, depth=2, report=False):
    print(f"\n[+] Analizuję adres Bitcoin: {address}\n")

    url = f"https://api.blockchair.com/bitcoin/dashboards/address/{address}"

    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print(f"[BŁĄD] Błąd zapytania: {response.status_code}")
            return

        resp = response.json()
        if not resp or 'data' not in resp or address not in resp['data']:
            print("[BŁĄD] Nieprawidłowa odpowiedź lub brak danych.")
            return

    except Exception as e:
        print(f"[BŁĄD] Wyjątek przy pobieraniu danych: {e}")
        return

    summary = resp['data'][address]['address']
    txs = resp['data'][address]['transactions']

    balance_btc = int(summary['balance']) / 1e8
    print(f"💰 Saldo BTC: {balance_btc:.8f} BTC")
    print(f"📄 Transakcji: {len(txs)} (pokażę maks. 5):\n")

    for tx in txs[:5]:
        print(f"➡️  TXID: {tx[:16]}...")

    # ZAPISZ CSV
    os.makedirs("reports", exist_ok=True)
    output_file = f"reports/{address}_btc_tx.csv"
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['txid'])
        for tx in txs:
            writer.writerow([tx])

    print(f"\n📁 Zapisano dane do: {output_file}\n")

    if report:
        print("📝 [!] Moduł raportu PDF będzie dostępny w kolejnych krokach.")
