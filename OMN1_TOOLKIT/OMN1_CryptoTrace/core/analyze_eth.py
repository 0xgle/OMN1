import requests
import csv
import os

ETHERSCAN_API_KEY = "YOURAPIKEY"

def analyze_eth_address(address, depth=2, report=False):
    print(f"\n[+] Analizuję adres Ethereum: {address}\n")

    # SALDO ETH
    balance_url = (
        f"https://api.etherscan.io/api"
        f"?module=account&action=balance"
        f"&address={address}&tag=latest"
        f"&apikey={ETHERSCAN_API_KEY}"
    )
    response = requests.get(balance_url).json()
    if response["status"] != "1":
        print("[BŁĄD] Nie udało się pobrać salda:", response["message"])
        return

    balance_wei = int(response["result"])
    balance_eth = balance_wei / 10**18
    print(f"💰 Saldo ETH: {balance_eth:.6f} ETH")

    # TRANSAKCJE
    tx_url = (
        f"https://api.etherscan.io/api"
        f"?module=account&action=txlist"
        f"&address={address}"
        f"&startblock=0&endblock=99999999"
        f"&sort=desc"
        f"&apikey={ETHERSCAN_API_KEY}"
    )
    tx_response = requests.get(tx_url).json()
    if tx_response["status"] != "1":
        print("[BŁĄD] Nie udało się pobrać transakcji:", tx_response["message"])
        return

    txs = tx_response.get("result", [])
    print(f"\n📄 Transakcji: {len(txs)} (pokażę maks. 5):\n")
    for tx in txs[:5]:
        direction = "⬆️  OUT" if tx["from"].lower() == address.lower() else "⬇️  IN"
        value_eth = int(tx["value"]) / 10**18
        print(f"[{direction}] {tx['hash'][:12]}... | {value_eth:.4f} ETH | do: {tx['to']}")

    # ZAPISZ CSV
    os.makedirs("reports", exist_ok=True)
    output_file = f"reports/{address}_eth_tx.csv"
    with open(output_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["hash", "from", "to", "value_eth", "timestamp"])
        for tx in txs:
            value_eth = int(tx["value"]) / 10**18
            writer.writerow([tx["hash"], tx["from"], tx["to"], value_eth, tx["timeStamp"]])

    print(f"\n📁 Zapisano dane do: {output_file}\n")

    if report:
        print("📝 [!] Moduł raportu PDF będzie dostępny w kolejnych krokach.")
