# core/out_trace.py

from core.utils import get_eth_transactions

def trace_out(address, api_key, limit=10):
    print(f"\n🔎 Śledzenie gdzie wysłano środki z: {address}\n")

    transactions = get_eth_transactions(address, api_key, direction="out", limit=limit)
    if not transactions:
        print("[!] Brak transakcji OUT.")
        return

    for tx in transactions:
        print(f"⬆️  {address} → TO: {tx['to'][:12]}... | {tx['value']} ETH")
