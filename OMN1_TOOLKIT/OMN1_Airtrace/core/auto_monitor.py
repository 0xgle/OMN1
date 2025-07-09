# core/auto_monitor.py

import subprocess
import re
import time

def kill_conflicting_processes():
    """Kill processes that interfere with monitor mode."""
    print("[*] Checking for interfering processes...")
    try:
        result = subprocess.check_output(['airmon-ng', 'check'], stderr=subprocess.DEVNULL).decode()
        pids = re.findall(r'^\s*(\d+)\s', result, re.MULTILINE)
        if pids:
            print(f"[!] Killing {len(pids)} interfering processes: {', '.join(pids)}")
            subprocess.run(['airmon-ng', 'check', 'kill'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            print("[+] No interfering processes found.")
    except Exception as e:
        print(f"[!] Failed to check/kill interfering processes: {e}")

def get_wireless_interfaces():
    """List all wireless interfaces that support monitor mode."""
    interfaces = []
    try:
        output = subprocess.check_output(['iw', 'dev'], stderr=subprocess.DEVNULL).decode()
        matches = re.findall(r'Interface\s+(\w+)', output)
        interfaces = list(set(matches))  # Remove duplicates
    except Exception as e:
        print(f"[!] Failed to get wireless interfaces: {e}")
    return interfaces

def enable_monitor_mode():
    """Enable monitor mode on the first available wireless interface."""
    kill_conflicting_processes()

    interfaces = get_wireless_interfaces()
    if not interfaces:
        print("[!] No wireless interfaces found.")
        return None

    for iface in interfaces:
        print(f"[*] Attempting to enable monitor mode on {iface}...")
        try:
            result = subprocess.run(['airmon-ng', 'start', iface], capture_output=True, text=True)
            if "monitor mode vif enabled" in result.stdout or "monitor mode enabled" in result.stdout:
                monitor_iface = iface + "mon" if not iface.endswith("mon") else iface
                print(f"[+] Monitor mode enabled on {monitor_iface}")
                return monitor_iface
            elif "monitor mode already enabled" in result.stdout:
                print(f"[+] Monitor mode already enabled on {iface}")
                return iface
        except Exception as e:
            print(f"[!] Failed to enable monitor mode on {iface}: {e}")

    print("[!] Could not enable monitor mode on any interface.")
    return None
