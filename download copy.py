# Importing necessary libraries
from flask import Flask, render_template, request, send_file
import csv
from io import StringIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Flask app initialization
app = Flask(__name__)

# Data storage
# A list to store transactions (this could be a database in a real-world scenario)
transactions = []

# Bank statement route
@app.route("/", methods=["GET", "POST"])
def bank_statement():
    """
    Main route to render the bank statement form and process form data
    to handle transactions. Calculates balances and checks for
    insufficient funds on debit transactions.
    """
    error_message = None  # Variable to store error messages

    if request.method == "POST":
        # Get transaction details from the form
        date = request.form["date"]
        description = request.form["description"]
        transaction_type = request.form["type"]
        amount = float(request.form["amount"])

        # Check if the transaction is a debit and if the balance is sufficient
        if transaction_type == "debit":
            if len(transactions) == 0 or transactions[-1]["balance"] < amount:
                error_message = "Insufficient balance to complete this transaction."
            else:
                last_balance = transactions[-1]["balance"]
                balance = last_balance - amount
        else:
            # Process a credit transaction
            last_balance = transactions[-1]["balance"] if transactions else 0
            balance = last_balance + amount

        # If no error, add the transaction to the list
        if error_message is None:
            transactions.append({
                "date": date,
                "description": description,
                "type": transaction_type,
                "amount": amount,
                "balance": balance
            })

    # Calculate total credits, debits, and final balance
    total_credit = sum([trans['amount'] for trans in transactions if trans['type'] == 'credit'])
    total_debit = sum([trans['amount'] for trans in transactions if trans['type'] == 'debit'])
    final_balance = transactions[-1]["balance"] if transactions else 0

    return render_template("download.html", transactions=transactions, 
                           total_credit=total_credit, total_debit=total_debit, 
                           final_balance=final_balance, error_message=error_message)

# CSV Download Route
@app.route("/download/csv")
def download_csv():
    """
    Creates and sends a CSV file of the transaction data.
    """
    # Create a string IO object to write CSV data
    si = StringIO()
    csv_writer = csv.writer(si)
    csv_writer.writerow(["Date", "Description", "Type", "Debit (DR)", "Credit (CR)", "Balance"])

    # Write transaction data to CSV
    for transaction in transactions:
        debit = transaction['amount'] if transaction['type'] == 'debit' else ''
        credit = transaction['amount'] if transaction['type'] == 'credit' else ''
        csv_writer.writerow([transaction["date"], transaction["description"], transaction["type"], debit, credit, transaction["balance"]])

    # Move the pointer to the beginning of the file for sending
    si.seek(0)

    return send_file(si, mimetype="text/csv", as_attachment=True, download_name="bank_statement.csv")

# PDF Download Route
@app.route("/download/pdf")
def download_pdf():
    """
    Creates and sends a PDF file of the transaction data.
    """
    # Create a PDF
    pdf_filename = "/tmp/bank_statement.pdf"
    c = canvas.Canvas(pdf_filename, pagesize=letter)

    # Title of the PDF
    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, 750, "Bank Statement")

    # Set table header
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, 700, "Date")
    c.drawString(150, 700, "Description")
    c.drawString(250, 700, "Type")
    c.drawString(350, 700, "Debit (DR)")
    c.drawString(450, 700, "Credit (CR)")
    c.drawString(550, 700, "Balance")

    # Write transaction details to the PDF
    y_position = 680
    for transaction in transactions:
        c.setFont("Helvetica", 9)
        debit = transaction['amount'] if transaction['type'] == 'debit' else ''
        credit = transaction['amount'] if transaction['type'] == 'credit' else ''
        
        c.drawString(50, y_position, transaction["date"])
        c.drawString(150, y_position, transaction["description"])
        c.drawString(250, y_position, transaction["type"].capitalize())
        c.drawString(350, y_position, str(debit))
        c.drawString(450, y_position, str(credit))
        c.drawString(550, y_position, str(transaction["balance"]))
        
        y_position -= 20  # Move down for the next row

    # Save the PDF
    c.save()

    return send_file(pdf_filename, mimetype='application/pdf', as_attachment=True, download_name="bank_statement.pdf")

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)