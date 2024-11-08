from flask import send_file
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from datetime import datetime
import random

# Your generate_pdf function...

# Get today's date in the format YYYY-MM-DD
date_today = datetime.today().strftime('%Y-%m-%d')
# Generate a batch number that starts with '1' and is followed by three random digits
batch_number = f"1{random.randint(100, 999)}"

def generate_pdf(journal_entries):
    pdf_buffer = BytesIO()

    # Set the PDF page size to landscape letter
    c = canvas.Canvas(pdf_buffer, pagesize=landscape(letter))
    width, height = landscape(letter)

    # Title and metadata
    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, height - 50, "Journal Entries Report")
    
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 70, f"Batch Number: {batch_number}")
    c.drawString(400, height - 70, f"Date: {date_today}")

    # Table data
    styles = getSampleStyleSheet()
    data = [[
        Paragraph('Name', styles['BodyText']),
        Paragraph('Account Number', styles['BodyText']),
        Paragraph('Transaction Type', styles['BodyText']),
        Paragraph('Debit', styles['BodyText']),
        Paragraph('Credit', styles['BodyText'])
    ]]

    # Initialize total variables
    total_debit = 0.0
    total_credit = 0.0

    # Add journal entry rows to the table and calculate totals
    for entry in journal_entries:
        debit = float(entry['debit']) if entry['debit'] else 0.0
        credit = float(entry['credit']) if entry['credit'] else 0.0
        
        total_debit += debit
        total_credit += credit

        data.append([
            Paragraph(entry['name'], styles['BodyText']),
            Paragraph(entry['account_number'], styles['BodyText']),
            Paragraph(entry['transaction_type'], styles['BodyText']),
            Paragraph(f"{debit:,.2f}", styles['BodyText']),
            Paragraph(f"{credit:,.2f}", styles['BodyText'])
        ])

    # Add a row for the totals at the bottom
    data.append([
        Paragraph('TOTAL', styles['BodyText']),
        Paragraph('', styles['BodyText']),
        Paragraph('', styles['BodyText']),
        Paragraph(f"{total_debit:,.2f}", styles['BodyText']),
        Paragraph(f"{total_credit:,.2f}", styles['BodyText'])
    ])

    # Adjust column widths for better alignment
    column_widths = [180, 150, 120, 100, 100]

    # Table formatting
    table = Table(data, colWidths=column_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4F81BD")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'), 
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#D9E1F2")),
    ]))

    # Table positioning and finalizing PDF
    table.wrapOn(c, width, height)
    table.drawOn(c, (width - sum(column_widths)) / 2, (height - len(data) * 20) / 2)

    c.showPage()
    c.save()
    pdf_buffer.seek(0)

    return send_file(
        pdf_buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name="journal_entries.pdf"
    )