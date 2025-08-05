# PINCRUSHER_ULTIMATE

**Author:** 0xgle  
**License:** MIT  

> **Disclaimer:**  
> This tool is intended for **authorized security testing** and **CTF challenges** only.  
> Do not use on systems you do not own or do not have explicit permission to test.

---

## 🛠 Overview

`PINCRUSHER_ULTIMATE` is all-in-one OTP/PIN brute-forcer designed for **CTF** and **authorized penetration testing**.

Features:

- **Modes**:
  - `STRICT` – Per-attempt fresh token, sequential, rate-limit aware
  - `FAST` – Multi-threaded, best-effort detection for simple endpoints
- **Sources**:
  - Numeric PIN ranges (e.g., 0000..9999)
  - Wordlists (custom strings)
- **Advanced detection**:
  - Success/fail heuristics
  - Optional success phrase check
  - Baseline probe & debug dumps
- **Anti-rate-limit**:
  - Delay + jitter
  - Backoff retries
  - Rotate cookies/proxies
  - Random `X-Forwarded-For`
- **Input options**:
  - Single cookie or cookie list (`cookies.txt`)
  - Proxy list (`proxies.txt`)
  - Wordlist or PIN range
- **Output**:
  - JSONL logs
  - Resume from previous run
  - Save found code to file
- **Interfaces**:
  - CLI with full argument support
  - Interactive CLI (no args)
  - GUI (Tkinter)

---

## 📦 Installation

### Requirements
- Python 3.8+
- `pip install requests rich beautifulsoup4`

On Debian/Ubuntu:
```bash
sudo apt install python3 python3-pip python3-tk
pip install requests rich beautifulsoup4


▶️ Usage
CLI Mode
Strict mode (default)

python omn1_pincrusher.py \
  --target 10.10.160.160:1337 \
  --mode strict \
  --cookie "PHPSESSID=abc123" \
  --pin-len 4 \
  --rotate-xff

Fast mode

python omn1_pincrusher.py \
  --target 10.10.160.160:1337 \
  --mode fast \
  --cookie "PHPSESSID=abc123" \
  --static-token 179 \
  --pin-len 4
  
💡 Examples

  
Brute-force with cookies list and proxy list:

python omn1_pincrusher.py \
  --target 10.10.160.160:1337 \
  --mode strict \
  --cookie-file cookies.txt \
  --proxy-file proxies.txt \
  --pin-len 6 \
  --rotate-every 20 \
  --rotate-xff

Resume from previous run:

python omn1_pincrusher.py \
  --target 10.10.160.160:1337 \
  --resume logs.jsonl
  
  
📜 License

MIT License © 0xgle

