#!/usr/bin/env python3
"""
OMN1_SNIPPET – junior-friendly cheat-sheet launcher with search
Author: mgledev
"""

import os, sys, json, textwrap, re, termios, tty

BANNER = r"""
 ██████╗ ███╗   ███╗███╗   ██╗ ██╗
██╔═══██╗████╗ ████║████╗  ██║███║
██║   ██║██╔████╔██║██╔██╗ ██║╚██║
██║   ██║██║╚██╔╝██║██║╚██╗██║ ██║
╚██████╔╝██║ ╚═╝ ██║██║ ╚████║ ██║
 ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═══╝ ╚═╝   SNIPPET by 0xgle
"""

SNIPPET_DIR = os.path.join(os.path.dirname(__file__), "snippets")


# ───────────────────────────── utils ──────────────────────────────── #
def read_key() -> str:
    """Read single keystroke (no ENTER needed)."""
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def load_snippet_file(fname: str) -> dict:
    with open(os.path.join(SNIPPET_DIR, fname), encoding="utf-8") as f:
        return json.load(f)


def load_all_snippets() -> list[dict]:
    return [load_snippet_file(f) for f in sorted(os.listdir(SNIPPET_DIR)) if f.endswith(".json")]


def show_snippet(snip: dict) -> None:
    print(f"\n📚  {snip['category']}  –  {snip.get('description','')}\n")
    for item in snip["cheats"]:
        print(f"🔹 {item['title']}")
        print(textwrap.indent(item["content"].rstrip(), "    "))
        if "source" in item:
            print(f"    ↳ {item['source']}")
        print()


def highlight(text: str, kw: str) -> str:
    # ANSI bold yellow
    return re.sub(re.escape(kw), f"\033[1;33m{kw}\033[0m", text, flags=re.IGNORECASE)


# ───────────────────────── main loop ──────────────────────────────── #
def menu_loop() -> None:
    files = sorted(f for f in os.listdir(SNIPPET_DIR) if f.endswith(".json"))
    while True:
        os.system("clear")
        print(BANNER)
        print("Select snippet pack:\n")
        for i, fn in enumerate(files, 1):
            cat = load_snippet_file(fn)["category"]
            print(f"  {i}) {cat}")
        print("  A) All packs")
        print("  S) Search keywords")
        print("  Q) Quit\n")
        print("👉  Press 1-{} | A | S | Q : ".format(len(files)), end="", flush=True)

        choice = read_key().lower()
        print()

        if choice == "q":
            print("\n👋  Bye!\n")
            break

        # show all packs
        if choice == "a":
            for fn in files:
                show_snippet(load_snippet_file(fn))
            input("\n🔙  ENTER to go back…")
            continue

        # search keywords
        if choice == "s":
            keyword = input("🔍  Enter keyword(s): ").strip()
            if not keyword:
                continue
            matches = []
            for snip in load_all_snippets():
                for item in snip["cheats"]:
                    blob = f"{snip['category']} {item['title']} {item['content']}".lower()
                    if keyword.lower() in blob:
                        matches.append((snip["category"], item))
            if not matches:
                input("\n⚠️  Nothing found – ENTER to continue…")
            else:
                print(f"\n🔎  Results for '{keyword}':\n")
                for cat, item in matches:
                    print(f"📂 {cat}  →  {highlight(item['title'], keyword)}")
                    preview = item["content"].splitlines()[0][:120]
                    print(f"    {highlight(preview, keyword)} …\n")
                input("🔙  ENTER to view packs menu…")
            continue

        # single pack
        if choice.isdigit() and 1 <= int(choice) <= len(files):
            show_snippet(load_snippet_file(files[int(choice) - 1]))
            input("\n🔙  ENTER to go back…")
            continue

        input("❌  Invalid selection – ENTER to retry…")


if __name__ == "__main__":
    menu_loop()
