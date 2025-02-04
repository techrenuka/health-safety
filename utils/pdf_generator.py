from fpdf import FPDF
import os

def generate_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    pdf.cell(200, 10, txt="Health & Safety Risk Assessment", ln=True, align="C")
    pdf.ln(10)

    pdf.cell(200, 10, txt="Risk Factors:", ln=True)
    for risk in data.get("risk_factors", []):
        pdf.multi_cell(0, 10, f"- {risk}")

    pdf.ln(10)
    pdf.cell(200, 10, txt="Safety Measures:", ln=True)
    for measure in data.get("safety_measures", []):
        pdf.multi_cell(0, 10, f"- {measure}")

    pdf_path = "reports/risk_assessment.pdf"
    pdf.output(pdf_path)
    return pdf_path