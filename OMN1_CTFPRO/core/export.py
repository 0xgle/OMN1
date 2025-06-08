# core/export.py – generowanie PDF raportu dla OMN1 CTFPRO

from fpdf import FPDF
import os
from core.task_manager import load_task

DATA_DIR = os.path.expanduser("~/.omn1_ctfpro")

def export_pdf(args):
    task = load_task(args.task)
    pdf = FPDF()
    pdf.add_page()

    # Logo i nagłówek
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="OMN1 CTFPRO REPORT", ln=True, align='C')
    pdf.set_font("Arial", '', 12)
    pdf.cell(200, 10, txt="Powered by mgledev", ln=True, align='C')

    # Logo graficzne
    logo_path = os.path.join(os.path.dirname(__file__), '../data/logo.png')
    if os.path.exists(logo_path):
        pdf.image(logo_path, x=150, y=10, w=40)

    pdf.ln(20)

    # Podstawowe informacje
    for key in ["name", "category", "difficulty", "ip", "created_at"]:
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(40, 10, txt=f"{key.capitalize()}: ", ln=False)
        pdf.set_font("Arial", '', 12)
        pdf.cell(100, 10, txt=str(task.get(key, '')), ln=True)

    # Recon
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="[Reconnaissance]", ln=True)
    pdf.set_font("Arial", '', 11)
    for r in task['recon']:
        pdf.multi_cell(0, 8, txt=f"- {r}")

    # Exploitation
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="[Exploitation]", ln=True)
    pdf.set_font("Arial", '', 11)
    for e in task['exploit']:
        pdf.multi_cell(0, 8, txt=f"- {e}")

    # Flagi
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="[Flags]", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.cell(0, 10, txt=f"User: {task['flag'].get('user', '')}", ln=True)
    pdf.cell(0, 10, txt=f"Root: {task['flag'].get('root', '')}", ln=True)

    # Zapis pliku
    out_path = os.path.join(DATA_DIR, f"{task['name'].replace(' ', '_')}_report.pdf")
    pdf.output(out_path)
    print(f"[+] Report saved to {out_path}")