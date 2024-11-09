from flask import send_file
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from datetime import datetime
import random

# Get today's date in the format YYYY-MM-DD
date_today = datetime.today().strftime('%Y-%m-%d')
# Generate a batch number that starts with '1' and is followed by three random digits
batch_number = f"1{random.randint(100, 999)}"

def generate_pdf(journal_entries):
    pdf_buffer = BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=landscape(letter))
    width, height = landscape(letter)

    # === HEADER SECTION ===
    # Draw header with date, table name, and batch number
    title_text = f"Date: {date_today}   |   Table: Journal Entries Report   |   Batch Number: {batch_number}"
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(width / 2, height - 40, title_text)

    # === BODY SECTION ===
    # Define styles for table content
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

    # Populate the table with journal entries and calculate totals
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

    # Adjust column widths
    column_widths = [180, 150, 120, 100, 100]

    # Create and style the main table
    table = Table(data, colWidths=column_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4F81BD")),  # Header background
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),                 # Header text color
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),                        # Center-align text
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),              # Bold header font
        ('FONTSIZE', (0, 0), (-1, -1), 10),                           # Font size
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),                        # Padding below header
        ('TOPPADDING', (0, 0), (-1, -1), 6),                          # Vertical cell padding
        ('GRID', (0, 0), (-1, -1), 1, colors.black),                  # Cell borders
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),                       # Vertical alignment to middle
    ]))

    # Position the table on the page
    table.wrapOn(c, width, height)
    table.drawOn(c, (width - sum(column_widths)) / 2, (height - len(data) * 20) / 2)

    # === FOOTER SECTION ===
    # Add totals row for Debit and Credit columns
    total_row = [
        Paragraph('TOTAL', styles['BodyText']),
        '', '',  # Empty columns for Name and Account Number
        Paragraph(f"{total_debit:,.2f}", styles['BodyText']),
        Paragraph(f"{total_credit:,.2f}", styles['BodyText'])
    ]
    # Add footer row with styling
    footer_table = Table([total_row], colWidths=column_widths)
    footer_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),             # Bold font for totals
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#D9E1F2")), # Background color for totals
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    # Position the footer below the main table
    footer_table.wrapOn(c, width, height)
    footer_table.drawOn(c, (width - sum(column_widths)) / 2, (height - len(data) * 20) / 2 - 30)

    # Finalize and save the PDF
    c.showPage()
    c.save()
    pdf_buffer.seek(0)

    return send_file(
        pdf_buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name="journal_entries.pdf"
    )