# core/in_trace.py

from core.utils import get_eth_transactions

def trace_in(address, api_key, limit=10):
    print(f"\n🔎 Śledzenie pochodzenia środków dla: {address}\n")

    transactions = get_eth_transactions(address, api_key, direction="in", limit=limit)
    if not transactions:
        print("[!] Brak transakcji IN.")
        return

    for tx in transactions:
        print(f"⬇️  FROM: {tx['from'][:12]}... → {address} | {tx['value']} ETH")
