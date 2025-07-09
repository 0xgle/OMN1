# core/utils.py
import requests

def get_vendor(mac):
    try:
        oui = mac.upper()[0:8].replace(":", "-")
        resp = requests.get(f"https://api.macvendors.com/{mac}")
        if resp.status_code == 200:
            return resp.text.strip()
        else:
            return "Unknown Vendor"
    except:
        return "Vendor Lookup Failed"
