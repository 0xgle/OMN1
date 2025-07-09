import time
from core import auto_monitor, live_sniffer

def print_logo():
    print(r"""
 ██████╗ ███╗   ███╗███╗   ██╗ ██╗
██╔═══██╗████╗ ████║████╗  ██║███║
██║   ██║██╔████╔██║██╔██╗ ██║╚██║
██║   ██║██║╚██╔╝██║██║╚██╗██║ ██║
╚██████╔╝██║ ╚═╝ ██║██║ ╚████║ ██║
 ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═══╝ ╚═╝  AirTrace by 0xgle
""")

def main_menu():
    print("Welcome to AirTrace - Real-time Wi-Fi Device Scanner")
    print("============================================================")
    print("[1] Start Live Wi-Fi Monitoring")
    print("[2] Exit\n")

def main():
    print_logo()
    main_menu()
    choice = input("Choose an option: ").strip()

    if choice == "1":
        print("\n[*] Initializing interface...")
        monitor_iface = auto_monitor.enable_monitor_mode()


        if not monitor_iface:
            print("\n[!] Failed to setup monitor interface. Exiting.")
            return

        print(f"[+] Monitor interface: {monitor_iface}")
        print(f"[*] Starting live Wi-Fi scan on {monitor_iface}... Press Ctrl+C to stop.\n")
        time.sleep(1)
        live_sniffer.start_live_scan(monitor_iface)

    elif choice == "2":
        print("Goodbye.")
    else:
        print("[!] Invalid choice. Try again.")

if __name__ == "__main__":
    main()
