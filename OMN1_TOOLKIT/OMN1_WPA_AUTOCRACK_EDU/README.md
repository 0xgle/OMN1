# 📡 OMN1_WPA_AUTOCRACK_EDU

**Educational WPA2 Handshake Capture & Crack Tool**  
Part of the [OMN1 Toolkit](https://github.com/mgledev/OMN1) by [mgledev](https://github.com/mgledev) – 2025

---

## 🎓 Description

`OMN1_WPA_AUTOCRACK_EDU` is an educational script that guides students step-by-step through the process of:

1. Enabling monitor mode
2. Capturing WPA2 beacons
3. Selecting a target access point
4. Capturing the WPA2 handshake using `airodump-ng`
5. Sending `deauth` frames with `aireplay-ng`
6. Cracking the handshake using `aircrack-ng` and a dictionary

The script runs everything in the terminal with two helper windows for real-time monitoring – making it a perfect **learning tool** for wireless security courses and labs.

---

## 🛠 Requirements

- Linux (recommended: Kali Linux)
- Python 3.x
- Tools: `airmon-ng`, `airodump-ng`, `aireplay-ng`, `aircrack-ng`, `konsole` or `xterm`
- Wireless card capable of monitor mode
- A wordlist (default: `rockyou.txt`)

---

## 🧪 Usage

```bash
sudo python3 omn1_wpa_autocrack.py
