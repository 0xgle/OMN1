# ========================
# MODUŁ: core/graph_builder.py
# ========================

# Generuje graf przepływu transakcji dla Ethereum lub Bitcoin na podstawie CSV z analyze_eth/analyze_btc
# Wymaga matplotlib + networkx

import csv
import os
import networkx as nx
import matplotlib.pyplot as plt

def build_graph_from_csv(csv_file, output_path="reports/graph.png"):
    if not os.path.exists(csv_file):
        print(f"[BŁĄD] Plik {csv_file} nie istnieje.")
        return

    G = nx.DiGraph()

    with open(csv_file, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            source = row.get('from', None)
            target = row.get('to', None)
            label = float(row.get('value_eth', 0)) if 'value_eth' in row else ""
            if source and target:
                G.add_edge(source, target, label=label)

    if not G.nodes:
        print("[!] Brak danych do stworzenia grafu.")
        return

    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G, k=0.3, iterations=30)
    nx.draw(G, pos, with_labels=False, node_size=500, node_color="skyblue", edge_color="gray")

    # etykiety krawędzi
    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)

    plt.title("Flow of Funds – OMN1_CryptoTrace")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path)
    plt.close()

    print(f"📊 Zapisano graf do: {output_path}")
