import requests

# Replace with your real server
SERVER_URL = "https://yourserver.com/upload"

def send_to_server(file_path):
    with open(file_path, "rb") as f:
        files = {"file": (file_path, f)}
        response = requests.post(SERVER_URL, files=files)
        if response.status_code == 200:
            print("[+] Report sent to server successfully.")
        else:
            print(f"[!] Failed to send report. Status: {response.status_code}")
