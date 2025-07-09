import os
import socket
import platform
import subprocess
import getpass
from datetime import datetime
import ctypes

def is_admin():
    """Check if the script is run with admin privileges"""
    try:
        return os.getuid() == 0
    except AttributeError:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0

def collect_info(output_file):
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("=== OMN1_Icebreaker Report (Windows) ===\n\n")
        f.write(f"Generated: {datetime.now()}\n")
        f.write(f"Username: {getpass.getuser()}\n")
        f.write(f"Hostname: {socket.gethostname()}\n")
        f.write(f"OS: {platform.platform()}\n")
        f.write(f"Is Admin: {is_admin()}\n\n")

        # SYSTEM INFO
        f.write("--- SYSTEM INFO ---\n")
        f.write(subprocess.getoutput("systeminfo"))
        f.write("\n")

        # INSTALLED SOFTWARE
        f.write("--- INSTALLED SOFTWARE ---\n")
        try:
            output = subprocess.check_output(['wmic', 'product', 'get', 'name,version'], stderr=subprocess.DEVNULL).decode()
            f.write(output)
        except:
            f.write("(Could not retrieve software list)\n")

        # NETWORK CONFIG
        f.write("\n--- NETWORK CONFIGURATION ---\n")
        f.write(subprocess.getoutput("ipconfig /all"))

        f.write("\n--- ROUTING TABLE ---\n")
        f.write(subprocess.getoutput("route print"))

        f.write("\n--- DNS CACHE ---\n")
        f.write(subprocess.getoutput("ipconfig /displaydns"))

        # PROCESSES
        f.write("\n--- RUNNING PROCESSES ---\n")
        f.write(subprocess.getoutput("tasklist /v"))

        # AUTORUN PROGRAMS
        f.write("\n--- AUTORUN PROGRAMS ---\n")
        f.write(subprocess.getoutput("wmic startup get caption,command"))

        # USER ACCOUNTS
        f.write("\n--- USER ACCOUNTS ---\n")
        f.write(subprocess.getoutput("net user"))

        # USB HISTORY
        f.write("\n--- USB DEVICES HISTORY ---\n")
        try:
            usb_output = subprocess.check_output(['reg', 'query', r'HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Enum\USBSTOR'], stderr=subprocess.DEVNULL).decode(errors='ignore')
            f.write(usb_output)
        except:
            f.write("(Could not read USB history)\n")

        # FIREWALL RULES
        f.write("\n--- FIREWALL RULES ---\n")
        f.write(subprocess.getoutput("netsh advfirewall firewall show rule name=all"))

        # AV DETECTION
        f.write("\n--- ANTIVIRUS DETECTION ---\n")
        try:
            av_output = subprocess.check_output(['powershell', '-Command', 'Get-CimInstance -Namespace root/SecurityCenter2 -ClassName AntivirusProduct'], stderr=subprocess.DEVNULL).decode()
            f.write(av_output)
        except:
            f.write("(Could not detect AV software)\n")

        # SUSPICIOUS TOOLS CHECK
        f.write("\n--- SUSPICIOUS TOOLS CHECK ---\n")
        keywords = ["tor", "metasploit", "keygen", "crack", "ransom", "stealer", "wireshark", "nmap", "aircrack", "cain"]
        found = []
        for prog in keywords:
            try:
                output = subprocess.check_output(["where", prog], stderr=subprocess.DEVNULL).decode(errors='ignore')
                found.append((prog, output))
            except:
                continue
        if found:
            for prog, path in found:
                f.write(f"Detected tool: {prog} → {path}\n")
        else:
            f.write("No known suspicious tools found.\n")

        # BROWSER DATA PATHS (just show paths for manual review)
        f.write("\n--- BROWSER DATA PATHS ---\n")
        appdata = os.getenv('APPDATA')
        localapp = os.getenv('LOCALAPPDATA')
        paths = [
            os.path.join(localapp, 'Google', 'Chrome', 'User Data', 'Default', 'History'),
            os.path.join(appdata, 'Mozilla', 'Firefox', 'Profiles')
        ]
        for path in paths:
            exists = os.path.exists(path)
            f.write(f"{path} → {'Exists' if exists else 'Not found'}\n")

        # END
        f.write("\n[✓] Report completed.\n")

