def is_target_allowed(target):
    try:
        with open("targets.txt") as f:
            allowed = [line.strip() for line in f]
        return target in allowed
    except:
        return False
