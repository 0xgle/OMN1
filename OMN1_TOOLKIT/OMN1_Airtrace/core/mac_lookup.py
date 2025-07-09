import csv
import os

OUI_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'oui.csv')

def load_oui_database():
    oui_dict = {}
    try:
        with open(OUI_FILE, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2:
                    prefix = row[0].strip().upper().replace("-", ":")
                    vendor = row[1].strip()
                    oui_dict[prefix] = vendor
    except FileNotFoundError:
        print("[!] OUI database not found. Manufacturer lookup disabled.")
    return oui_dict

def lookup_manufacturer(mac, oui_db):
    prefix = ":".join(mac.upper().split(":")[:3])
    return oui_db.get(prefix, "Unknown")
