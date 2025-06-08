# core/task_manager.py – zarządzanie zadaniami CTF w OMN1 CTFPRO

import os
import json
from datetime import datetime

DATA_DIR = os.path.expanduser("~/.omn1_ctfpro")
os.makedirs(DATA_DIR, exist_ok=True)

def get_task_path(task_name):
    return os.path.join(DATA_DIR, f"{task_name.replace(' ', '_')}.json")

def save_task(task):
    path = get_task_path(task['name'])
    with open(path, 'w') as f:
        json.dump(task, f, indent=4)

def load_task(task_name):
    path = get_task_path(task_name)
    if not os.path.exists(path):
        print(f"[!] Task '{task_name}' not found.")
        exit(1)
    with open(path, 'r') as f:
        return json.load(f)

def add_task(args):
    task = {
    "name": args.name,
    "difficulty": args.difficulty,
    "ip": args.ip or "",
    "created_at": datetime.now().isoformat(),
    "recon": [],
    "exploit": [],
    "flag": {"user": "", "root": ""}
}

    save_task(task)
    print(f"[+] Task '{args.name}' added.")

def list_tasks(_args=None):
    if not os.path.exists(DATA_DIR):
        print("📁 Brak zadań – katalog ~/.omn1_ctfpro nie istnieje.")
        return

    tasks = [f for f in os.listdir(DATA_DIR) if f.endswith(".json")]
    if not tasks:
        print("📂 Brak zadań w systemie.")
        return

    print("📋 Lista zadań:")
    for task_file in tasks:
        path = os.path.join(DATA_DIR, task_file)
        with open(path, 'r') as f:
            task = json.load(f)
            user_flag = task.get("flag", {}).get("user", "") or "❌"
            root_flag = task.get("flag", {}).get("root", "") or "❌"
            print(f"[{task['name']}]  🧠 {task['difficulty']}  🌐 {task['ip']}  🏁 user: {user_flag} | root: {root_flag}")




def show_task(args):
    task = load_task(args.task)
    print(json.dumps(task, indent=4))

def set_flag(args):
    task = load_task(args.task)
    if args.user:
        task['flag']['user'] = args.user
    if args.root:
        task['flag']['root'] = args.root
    save_task(task)
    print(f"[+] Flag(s) saved for '{args.task}'.")
