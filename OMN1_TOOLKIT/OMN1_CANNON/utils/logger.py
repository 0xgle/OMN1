def log_event(msg):
    from datetime import datetime
    with open("omni_cannon.log", "a") as f:
        f.write(f"[{datetime.now()}] {msg}\n")
