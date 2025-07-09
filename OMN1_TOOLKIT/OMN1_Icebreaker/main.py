import os
import platform
from datetime import datetime

try:
    from core import collector_linux
except ImportError:
    collector_linux = None

try:
    from core import collector_win
except ImportError:
    collector_win = None

def main():
    print("[*] Running OMN1_Icebreaker...")

    # Generuj nazwę pliku raportu
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"report_{timestamp}.txt"

    # Wykryj system operacyjny
    current_os = platform.system()
    print(f"[+] Detected OS: {current_os}")

    try:
        if current_os == "Linux" and collector_linux:
            collector_linux.collect_info(report_filename)
        elif current_os == "Windows" and collector_win:
            collector_win.collect_info(report_filename)
        else:
            print(f"[!] Unsupported OS or collector module missing: {current_os}")
            return

        print(f"[+] Report saved to {report_filename}")

    except Exception as e:
        print(f"[!] Error collecting data: {str(e)}")

if __name__ == "__main__":
    main()
