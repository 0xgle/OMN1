def load_targets(filepath="targets.txt"):
    try:
        with open(filepath, "r") as f:
            lines = f.readlines()
            return [line.strip() for line in lines if line.strip()]
    except FileNotFoundError:
        print(f"[!] Target file not found: {filepath}")
        return []
