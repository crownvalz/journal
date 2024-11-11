from flask import Flask, render_template, request, send_file
from utils import load_csv_data, append_to_csv
from pdf_utils import generate_pdf
from csv_utils import generate_csv
import random
from datetime import datetime
app = Flask(__name__)

# Paths to CSV files
JOURNAL_CSV = 'journal_entries.csv'
CUSTOMER_CSV = 'customer_data.csv'
GL_CSV = 'gl_data.csv'

# Load customer and GL data
customers = load_csv_data(CUSTOMER_CSV)
gl_codes = load_csv_data(GL_CSV)

@app.route("/", methods=["GET", "POST"])
def journal_entry():
    journal_entries = load_csv_data(JOURNAL_CSV)

    if request.method == "POST":
        account_type = request.form["account_type"]
        nature_of_transaction = request.form["nature_of_transaction"]
        amount = float(request.form["amount"])

        debit = str(amount) if nature_of_transaction == "Debit" else ""
        credit = str(amount) if nature_of_transaction == "Credit" else ""

        if account_type == "customer":
            account_number = request.form["customer_account"]
            name = next(customer['Customer Name'] for customer in customers if customer['Account Number'] == account_number)
        else:
            account_number = request.form["gl_account"]
            name = next(gl['GL Name'] for gl in gl_codes if gl['GL Code'] == account_number)

        new_entry = {
            "name": name,
            "account_number": account_number,
            "transaction_type": nature_of_transaction,
            "debit": debit,
            "credit": credit
        }

        append_to_csv(JOURNAL_CSV, new_entry)

    total_debit = sum(float(entry['debit']) for entry in journal_entries if entry['debit'])
    total_credit = sum(float(entry['credit']) for entry in journal_entries if entry['credit'])

    return render_template(
        "index.html",
        journal_entries=journal_entries,
        customers=customers,
        gl_codes=gl_codes,
        total_debit=total_debit,
        total_credit=total_credit
    )

@app.route("/download/csv")
def download_csv():
    journal_entries = load_csv_data(JOURNAL_CSV)
    return generate_csv(journal_entries)

@app.route("/download/pdf")
def download_pdf():
    journal_entries = load_csv_data(JOURNAL_CSV)
    return generate_pdf(journal_entries)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)