import os
import streamlit as st
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.analyze_eth import analyze_eth_address
from core.analyze_btc import analyze_btc_address
from core.flow_trace import build_graph
from core.graph_builder import build_graph_from_csv
from core.report import generate_pdf_report

ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY", "YOURAPIKEY")

st.set_page_config(page_title="OMN1_CryptoTrace", layout="wide")
st.title("🔎 OMN1_CryptoTrace – Interfejs Graficzny")

# 🔘 wybór blockchaina
blockchain = st.radio("Wybierz blockchain:", ["Ethereum", "Bitcoin"], horizontal=True)

address = st.text_input("Wprowadź adres:")

limit = st.slider("Liczba transakcji do analizy:", min_value=1, max_value=100, value=10)

col1, col2, col3, col4 = st.columns(4)

# 🔍 ANALIZA ADRESU
if col1.button("🔍 Analizuj adres"):
    if not address:
        st.error("⚠️ Podaj adres.")
    elif blockchain == "Ethereum":
        analyze_eth_address(address, depth=2, report=True)
    elif blockchain == "Bitcoin":
        analyze_btc_address(address)

# 🧭 IN
if col2.button("🧭 Śledź IN"):
    if not address:
        st.error("⚠️ Podaj adres.")
    elif blockchain == "Ethereum":
        build_graph(address, ETHERSCAN_API_KEY, direction="in", limit_in=limit, limit_out=0, output_file="in_graph.html")
        st.components.v1.html(open("in_graph.html", "r", encoding="utf-8").read(), height=600)
    elif blockchain == "Bitcoin":
        csv_file = f"reports/{address}_btc_tx.csv"
        build_graph_from_csv(csv_file, output_path="btc_in_graph.html")
        st.components.v1.html(open("btc_in_graph.html", "r", encoding="utf-8").read(), height=600)

# 📤 OUT
if col3.button("📤 Śledź OUT"):
    if not address:
        st.error("⚠️ Podaj adres.")
    elif blockchain == "Ethereum":
        build_graph(address, ETHERSCAN_API_KEY, direction="out", limit_in=0, limit_out=limit, output_file="out_graph.html")
        st.components.v1.html(open("out_graph.html", "r", encoding="utf-8").read(), height=600)
    elif blockchain == "Bitcoin":
        csv_file = f"reports/{address}_btc_tx.csv"
        build_graph_from_csv(csv_file, output_path="btc_out_graph.html")
        st.components.v1.html(open("btc_out_graph.html", "r", encoding="utf-8").read(), height=600)

# 🔁 IN + OUT
if col4.button("🔁 Wizualizacja IN + OUT"):
    if not address:
        st.error("⚠️ Podaj adres.")
    elif blockchain == "Ethereum":
        build_graph(address, ETHERSCAN_API_KEY, direction="both", limit_in=limit, limit_out=limit, output_file="inout_graph.html")
        st.components.v1.html(open("inout_graph.html", "r", encoding="utf-8").read(), height=600)
    elif blockchain == "Bitcoin":
        csv_file = f"reports/{address}_btc_tx.csv"
        build_graph_from_csv(csv_file, output_path="btc_full_graph.html")
        st.components.v1.html(open("btc_full_graph.html", "r", encoding="utf-8").read(), height=600)

# 📝 RAPORT
st.markdown("---")
if st.button("📝 Wygeneruj raport PDF"):
    generate_pdf_report()
    st.success("📄 Raport PDF wygenerowany w katalogu `reports/`.")
