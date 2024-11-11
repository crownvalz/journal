from flask import send_file
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from datetime import datetime
import random
from PIL import Image as PILImage

# Constants and reusable variables
logo_path = "company_logo.png"  # Path to company logo
company_name = "Self4me Solutions"
company_address = "1234 Business Rd, Dar es Salaam, Tanzania"

# Date and batch number
date_today = datetime.today().strftime('%Y-%m-%d')
batch_number = f"12{random.randint(10, 99)}"

# Table column widths for S/N, Name, Account Number, Transaction Type, Debit, and Credit
column_widths = [30, 180, 150, 120, 100, 100] 

# Styles and document setup
styles = getSampleStyleSheet()  # Predefined ReportLab styles

def generate_pdf(journal_entries):
    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=landscape(A4))  # Set to landscape A4
    elements = []  # Document elements

    # === HEADER SECTION ===
    # Company logo dimensions, maintaining aspect ratio
    with PILImage.open(logo_path) as img:
        orig_width, orig_height = img.size
    logo_width = 100
    logo_height = int((logo_width / orig_width) * orig_height)
    logo = Image(logo_path, width=logo_width, height=logo_height)
    elements.append(logo)

    # Company information and report title
    elements.append(Paragraph(company_name, styles['Title']))
    elements.append(Paragraph(company_address, styles['Normal']))
    elements.append(Spacer(1, 10))
    title_text = f"<b>Date:</b> {date_today} | <b>Journal Entries Report</b> | <b>Batch Number:</b> {batch_number}"
    elements.append(Paragraph(title_text, styles['Normal']))
    elements.append(Spacer(1, 20))

    # === BODY SECTION ===
    # Define table header
    data = [['S/N', 'Name', 'Account Number', 'Transaction Type', 'Debit', 'Credit']]
    total_debit = total_credit = 0.0
    serial_number = 1

    # Populate table rows with entries
    for entry in journal_entries:
        debit = float(entry['debit']) if entry['debit'] else 0.0
        credit = float(entry['credit']) if entry['credit'] else 0.0
        total_debit += debit
        total_credit += credit
        data.append([
            serial_number, entry['name'], entry['account_number'], entry['transaction_type'],
            f"{debit:,.2f}", f"{credit:,.2f}"
        ])
        serial_number += 1

    # Table style and data
    table = Table(data, colWidths=column_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4F81BD")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)

    # === FOOTER SECTION ===
    # Total row styling
    total_row = ['', '', '', 'TOTAL', f"{total_debit:,.2f}", f"{total_credit:,.2f}"]
    footer_table = Table([total_row], colWidths=column_widths)
    footer_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#D9E1F2")),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(footer_table)

    # Signature lines
    elements.append(Spacer(1, 30))
    elements.append(Paragraph("Prepared by: ________________________________", styles['Normal']))
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Checked by: ________________________________", styles['Normal']))
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Approved by: ________________________________", styles['Normal']))

    # Build document
    doc.build(elements)

    pdf_buffer.seek(0)
    return send_file(
        pdf_buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name="journal_entries_with_signatures.pdf"
    )