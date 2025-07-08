# ========================
# MODUŁ: core/risk_engine.py
# ========================

# Ocena ryzyka adresu na podstawie występowania w znanych listach mixerów, scamów itd.

import json
import os

RISK_FLAGS = {
    "mixer": "HIGH",
    "scam": "HIGH",
    "darknet": "HIGH",
    "exchange": "LOW",
    "normal": "LOW"
}

def load_list(path):
    try:
        with open(path) as f:
            return set(json.load(f))
    except:
        return set()

def assess_risk(address):
    address = address.lower()

    mixers = load_list("data/known_mixers.json")
    scams = load_list("data/scam_addresses.json")

    if address in mixers:
        return RISK_FLAGS["mixer"], "Znaleziono w liście mixerów."
    elif address in scams:
        return RISK_FLAGS["scam"], "Zidentyfikowany jako scam wallet."
    else:
        return RISK_FLAGS["normal"], "Brak znanych zagrożeń."

def batch_assess(csv_input, csv_output):
    import csv
    if not os.path.exists(csv_input):
        print("[BŁĄD] Nie znaleziono pliku CSV do analizy ryzyka.")
        return

    with open(csv_input, newline='') as fin, open(csv_output, 'w', newline='') as fout:
        reader = csv.DictReader(fin)
        fieldnames = reader.fieldnames + ['risk_level', 'risk_reason']
        writer = csv.DictWriter(fout, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            addr = row.get('to') or row.get('from')
            risk, reason = assess_risk(addr)
            row['risk_level'] = risk
            row['risk_reason'] = reason
            writer.writerow(row)

    print(f"📌 Ocena ryzyka zapisana w: {csv_output}")
