# 🛠 OMN1_TOOLKIT

**OMN1_TOOLKIT** is a curated collection of red-team and offensive security tools developed as part of the OMN1 framework by **mgledev**.

These tools are designed to assist during **penetration testing**, **CTFs**, **incident response**, **threat analysis**, and **red-team operations** — all written with clarity, modularity, and extensibility in mind.

---

## 📦 Included Tools

### 1. 🔍 DumpFerret  
**Credential leak scanner and dump analyzer**

- Automatic hash extraction & identification  
- Cracking support via John the Ripper  
- Data enrichment (HaveIBeenPwned, VirusTotal, AbuseIPDB)  
- Exports reports to PDF / CSV  
- Optional Streamlit GUI interface  

➡️ Folder: `OMN1_TOOLKIT/DumpFerret/`

---

### 2. 🕵️ LeakHunter  
**Secret & credential hunting tool**

- Searches GitHub repos, Pastebin-style dumps, local files  
- Flags hardcoded secrets, API keys, leaked credentials  
- Regex-driven scanning with false-positive filters  

➡️ Folder: `OMN1_TOOLKIT/LeakHunter/`

---

### 3. 📡 OMN1_WPA_AUTOCRACK_EDU  
**Wi-Fi handshake capture and password cracking (educational)**

- Monitor mode activation  
- Passive beacon scan + CSV export  
- Handshake capture + deauth + aircrack-ng  
- Designed to be used step-by-step by students  
- Fully annotated for learning purposes  

➡️ Folder: `OMN1_TOOLKIT/OMN1_WPA_AUTOCRACK_EDU/`

---

### 4. 🧠 OMN1_CryptoTrace  
**Blockchain investigation & visualization tool**

- Analyze Ethereum and Bitcoin addresses  
- Visualize transaction flow (IN/OUT) with graphing tools  
- Drill-down capability: click and trace new addresses  
- Risk scoring, scam detection, tagging  
- Streamlit GUI + pyvis network visualization  
- Generates audit-ready PDF reports  

➡️ Folder: `OMN1_TOOLKIT/OMN1_CryptoTrace/`

---

### 5. 🧊 OMN1_Icebreaker  
**USB-launchable recon and incident triage utility**

- Collects full system intelligence (OS, users, software, AV, network)  
- Detects suspicious software (cracks, stealer, Tor, etc.)  
- Extracts browser history, USB device history, autoruns, firewall rules  
- Works in **user** and **admin** mode  
- Generates plaintext or encrypted forensic reports  
- Two modes: local (write to USB) or remote (send to server)  
- Cross-platform: Windows and Linux versions available  

➡️ Folder: `OMN1_TOOLKIT/OMN1_Icebreaker/`

---

## 📜 License

This toolkit is part of the **OMN1 framework** and is released under the **MIT License**.  
You are free to **use**, **modify**, and **share** it for personal or professional purposes — just give credit to **mgledev**.

---

## 🚀 Author

**Made with ❤️ by [0xgle](https://github.com/mgledev)**  
Security enthusiast, builder of offensive tools & automation.  
_"Think like an attacker, act like a guardian."_
