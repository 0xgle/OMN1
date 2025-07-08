# core/report.py

from fpdf import FPDF
import os
import csv

def generate_pdf_report(input_csv="reports", output_pdf="reports/raport.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Raport Analizy Blockchain – OMN1_CryptoTrace", ln=True, align="C")

    folder = input_csv
    if not os.path.exists(folder):
        print("[BŁĄD] Folder 'reports/' nie istnieje.")
        return

    for filename in os.listdir(folder):
        if filename.endswith(".csv"):
            path = os.path.join(folder, filename)
            pdf.ln(10)
            pdf.set_font("Arial", "B", size=12)
            pdf.cell(200, 10, txt=f"📄 {filename}", ln=True)

            with open(path, newline='') as f:
                reader = csv.reader(f)
                headers = next(reader, [])
                pdf.set_font("Arial", size=10)
                for row in reader:
                    line = " | ".join(row)
                    pdf.cell(200, 8, txt=line[:100], ln=True)  # limit długości linii

    os.makedirs("reports", exist_ok=True)
    pdf.output(output_pdf)
    print(f"📄 Wygenerowano raport PDF: {output_pdf}")
