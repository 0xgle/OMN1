import csv
from scapy.all import sniff, Dot11
from datetime import datetime

seen_devices = set()

log_file = "devices_log.csv"

# Initialize CSV header if not exists
with open(log_file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Time", "MAC", "SSID", "Signal", "Frame Type"])

def handle_packet(pkt):
    if not pkt.haslayer(Dot11):
        return

    mac = pkt.addr2
    if mac is None or mac in seen_devices:
        return

    signal_strength = pkt.dBm_AntSignal if hasattr(pkt, 'dBm_AntSignal') else "N/A"
    frame_type = pkt.type
    subtype = pkt.subtype
    ssid = ""
    label = ""

    if frame_type == 0:  # Management frames
        if subtype == 8:  # Beacon frame
            ssid = pkt.info.decode(errors='ignore')
            label = "📡 Beacon"
        elif subtype == 4:  # Probe Request
            ssid = pkt.info.decode(errors='ignore') if hasattr(pkt, 'info') else ""
            label = "🔍 Probe Request"
        elif subtype == 0:  # Association request
            label = "🔌 Association Request"
        elif subtype == 11:  # Authentication
            label = "🔐 Authentication"
        else:
            label = "📶 Mgmt Frame"
    elif frame_type == 2:
        label = "📲 Data Frame"
    else:
        label = "❓ Other Frame"

    seen_devices.add(mac)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"[NEW] {label}: MAC={mac} | SSID={ssid} | Signal={signal_strength}dBm")

    with open(log_file, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, mac, ssid, signal_strength, label])

def start_live_scan(interface):
    print(f"[*] Starting live Wi-Fi scan on {interface}... Press Ctrl+C to stop.\n")
    sniff(iface=interface, prn=handle_packet, store=0)
