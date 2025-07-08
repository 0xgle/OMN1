from pyvis.network import Network
from core.utils import get_eth_transactions
import math

def build_graph(address, api_key, direction="both", limit_in=5, limit_out=5, output_file="graph.html"):
    """
    Tworzy interaktywny wykres transakcji Ethereum (IN/OUT) z wagą krawędzi od wartości ETH.
    """

    net = Network(height="700px", width="100%", bgcolor="#111111", font_color="white", directed=True)
    net.barnes_hut()

    net.add_node(address, label=address[:10] + "...", color="yellow")

    # INCOMING
    if direction in ("in", "both"):
        transactions_in = get_eth_transactions(address, api_key, direction="in", limit=limit_in)
        for tx in transactions_in:
            sender = tx["from"]
            value = tx["value"]
            if value <= 0:
                continue
            net.add_node(sender, label=sender[:10] + "...", color="green")

            width = scale_width(value)
            net.add_edge(sender, address,
                         title=f"{value} ETH",
                         label=f"{value} ETH",
                         arrows="to",
                         color="lime",
                         width=width)

    # OUTGOING
    if direction in ("out", "both"):
        transactions_out = get_eth_transactions(address, api_key, direction="out", limit=limit_out)
        for tx in transactions_out:
            recipient = tx["to"]
            value = tx["value"]
            if value <= 0:
                continue
            net.add_node(recipient, label=recipient[:10] + "...", color="red")

            width = scale_width(value)
            net.add_edge(address, recipient,
                         title=f"{value} ETH",
                         label=f"{value} ETH",
                         arrows="to",
                         color="orange",
                         width=width)

    net.write_html(output_file)
    print(f"✅ Interaktywny wykres zapisano jako: {output_file}")

def scale_width(value):
    """
    Skaluje wartość ETH na grubość krawędzi.
    """
    if value < 0.01:
        return 1
    elif value < 0.1:
        return 2
    elif value < 1:
        return 3
    elif value < 10:
        return 4
    elif value < 100:
        return 6
    elif value < 1000:
        return 8
    else:
        return 10
