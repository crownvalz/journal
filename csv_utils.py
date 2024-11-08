from flask import send_file
import csv
from io import StringIO

def generate_csv(journal_entries):
    si = StringIO()
    writer = csv.DictWriter(si, fieldnames=['name', 'account_number', 'transaction_type', 'debit', 'credit'])
    writer.writeheader()
    writer.writerows(journal_entries)
    si.seek(0)

    return send_file(
        si,
        mimetype="text/csv",
        as_attachment=True,
        download_name="journal_entries.csv"
    )