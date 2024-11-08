import csv

# Load data from a CSV file
def load_csv_data(filename):
    try:
        with open(filename, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            return [row for row in reader]
    except FileNotFoundError:
        return []  # Return empty list if file doesn't exist

# Append data to a CSV file
def append_to_csv(filename, data):
    with open(filename, mode='a', newline='') as file:
        fieldnames = ['name', 'account_number', 'transaction_type', 'debit', 'credit']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        # Write header if file is empty
        if file.tell() == 0:
            writer.writeheader()
        
        writer.writerow(data)