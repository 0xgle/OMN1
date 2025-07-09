
import platform
import os
import getpass
import socket
import subprocess
from datetime import datetime

def run_command(command):
    try:
        return subprocess.check_output(command, shell=True, text=True)
    except subprocess.CalledProcessError:
        return "[!] Command failed."

def write_section(file, title, content):
    file.write(f"\n===== {title} =====\n")
    file.write(content + "\n")

def collect_info(report_path):
    with open(report_path, "w") as f:
        f.write("OMN1_Icebreaker - Linux System Report\n")
        f.write("="*40 + "\n")
        f.write(f"Date: {datetime.now()}\n\n")

        write_section(f, "System Information", run_command("uname -a"))
        write_section(f, "Hostname", socket.gethostname())
        write_section(f, "Current User", getpass.getuser())
        write_section(f, "Uptime", run_command("uptime"))
        write_section(f, "Logged-in Users", run_command("who"))
        write_section(f, "User Accounts (/etc/passwd)", run_command("cat /etc/passwd"))
        write_section(f, "Sudoers File (/etc/sudoers)", run_command("cat /etc/sudoers"))
        write_section(f, "Crontab Entries", run_command("crontab -l"))
        write_section(f, "Running Processes", run_command("ps aux"))
        write_section(f, "Installed Packages (dpkg)", run_command("dpkg -l | head -n 30"))
        write_section(f, "Network Configuration", run_command("ip addr"))
        write_section(f, "Active Connections", run_command("ss -tulnp | head -n 20"))
        write_section(f, "Routing Table", run_command("ip route"))
        write_section(f, "Mounted Filesystems", run_command("df -h"))
        write_section(f, "USB Devices", run_command("lsusb"))
        write_section(f, "Connected PCI Devices", run_command("lspci"))

        write_section(f, "Bash History", run_command("cat ~/.bash_history | tail -n 30"))
        write_section(f, "SSH Authorized Keys", run_command("cat ~/.ssh/authorized_keys"))
        write_section(f, "Suspicious Files (.torrent/.apk/.exe/.py/.sh/.key/.pem)",
            run_command("find /home -type f \( -iname '*.torrent' -o -iname '*.apk' -o -iname '*.exe' -o -iname '*.py' -o -iname '*.sh' -o -iname '*.key' -o -iname '*.pem' \) 2>/dev/null | head -n 30"))

        # Browser History (basic level)
        chrome_history_path = os.path.expanduser("~/.config/google-chrome/Default/History")
        firefox_history_path = os.path.expanduser("~/.mozilla/firefox")

        if os.path.exists(chrome_history_path):
            write_section(f, "Chrome History", f"Found: {chrome_history_path}")
        if os.path.isdir(firefox_history_path):
            write_section(f, "Firefox Profiles", run_command(f"ls {firefox_history_path}"))

        f.write("\n[+] End of report.\n")
