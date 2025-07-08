#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.analyze_eth import analyze_eth_address
from core.analyze_btc import analyze_btc_address
from core.report import generate_pdf_report
from core.in_trace import trace_in
from core.out_trace import trace_out
from core.flow_trace import build_graph

import webbrowser

ETHERSCAN_API_KEY = "YOURAPIKEY"

def menu():
    while True:
        print("\n🔷 OMN1_CryptoTrace – MENU GŁÓWNE")
        print("────────────────────────────────────────────")
        print("1. 🖥️ Uruchom interfejs graficzny (GUI Streamlit)")
        print("────────────────────────────────────────────")
        print("2. 📊 Wizualizacja przepływu IN/OUT (Ethereum)")
        print("────────────────────────────────────────────")
        print("3. 🔎 Analiza adresu Ethereum")
        print("4. 🪙 Analiza adresu Bitcoin")
        print("5. 🧭 Śledzenie IN (skąd przyszły środki)")
        print("6. 📤 Śledzenie OUT (gdzie wysłano środki)")
        print("7. 📝 Generuj raport PDF")
        print("────────────────────────────────────────────")
        print("0. ❌ Wyjdź")
        print("────────────────────────────────────────────")

        choice = input("Wybierz opcję [0–7]: ")

        if choice == "1":
            print("Uruchamianie GUI Streamlit...")
            os.system("streamlit run ui/gui_streamlit.py")

        elif choice == "2":
            address = input("Podaj adres Ethereum: ")
            print("[+] Generuję wykres przepływu IN/OUT...")
            build_graph(address, ETHERSCAN_API_KEY, direction="both", limit_in=10, limit_out=10, output_file="inout_graph.html")
            webbrowser.open("inout_graph.html")

        elif choice == "3":
            address = input("Podaj adres Ethereum: ")
            analyze_eth_address(address, ETHERSCAN_API_KEY)

        elif choice == "4":
            address = input("Podaj adres Bitcoin: ")
            analyze_btc_address(address)

        elif choice == "5":
            address = input("Podaj adres Ethereum: ")
            trace_in(address, ETHERSCAN_API_KEY)

        elif choice == "6":
            address = input("Podaj adres Ethereum: ")
            trace_out(address, ETHERSCAN_API_KEY)

        elif choice == "7":
            generate_pdf_report()

        elif choice == "0":
            print("Zamykanie programu... 🛑")
            break

        else:
            print("❗ Nieprawidłowy wybór. Spróbuj ponownie.")


if __name__ == "__main__":
    menu()
