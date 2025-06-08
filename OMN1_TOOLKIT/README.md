# 🛠 OMN1_TOOLKIT

**OMN1_TOOLKIT** is a curated collection of red-team and offensive security tools developed as part of the **OMN1 framework** by `mgledev`.

These tools are designed to assist during penetration testing, CTFs, and offensive operations — all written with clarity, modularity, and extensibility in mind.

---

## 📦 Included Tools

### 1. 🔍 DumpFerret

**Dump analysis & enrichment tool** that scans credential leaks and performs:

- Automatic hash extraction & identification  
- Hash cracking with John the Ripper  
- Integration with HIBP, VirusTotal, AbuseIPDB  
- PDF/CSV export of results  
- Optional Streamlit GUI  

➡️ **Folder:** `OMN1_TOOLKIT/DumpFerret/`


### 2. 🕵️ LeakHunter

Tool to **search for secrets** (e.g., API keys, credentials) in:

- Public GitHub repos  
- Pastebin-style dumps  
- Local text files and log folders  

➡️ **Folder:** `OMN1_TOOLKIT/LeakHunter/`


### 3. 📡 OMN1_WPA_AUTOCRACK_EDU

An **educational tool for capturing WPA2 handshakes and launching dictionary attacks**. Designed to walk students step-by-step through the attack:

- Enables monitor mode and surveys Wi-Fi networks  
- Passive 10-second beacon scan + CSV output  
- Spawns two terminal windows: capture & deauth  
- Cracks handshake using `aircrack-ng` + custom wordlist  
- Explained line by line for maximum learning value  

➡️ **Folder:** `OMN1_TOOLKIT/OMN1_WPA_AUTOCRACK_EDU/`

---

## 📜 License

This toolkit is part of the **OMN1 framework** and is released under the **MIT License**.  
You are free to use, modify, and share it for personal or professional purposes — just give credit to **mgledev**.

---

## 🚀 Author

**Made with ❤️ by [mgledev](https://github.com/mgledev)**  
Security enthusiast, builder of offensive tools & automation.
