import csv
import json
from collections import defaultdict
from datetime import datetime

def convert_csv_to_json(input_file, output_file):
    # Dictionary to store transactions grouped by month
    monthly_data = defaultdict(lambda: {
        'transactions': [],
        'total_spending': 0.0
    })
    
    # Read the CSV file with UTF-8-sig encoding to handle BOM
    with open(input_file, 'r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile, fieldnames=['Date', 'Description', 'Amount', 'Balance'])
        
        for row in reader:
            # Parse the date
            date = datetime.strptime(row['Date'], '%m/%d/%Y')
            month_key = date.strftime('%Y-%m')  # Format: 2025-04
            month_name = date.strftime('%B %Y')  # Format: April 2025
            
            # Create transaction object
            transaction = {
                'date': row['Date'],
                'description': row['Description'],
                'amount': float(row['Amount']),
                'balance': float(row['Balance'])
            }
            
            # Add to monthly data
            monthly_data[month_key]['month'] = month_name
            monthly_data[month_key]['transactions'].append(transaction)
            monthly_data[month_key]['total_spending'] += float(row['Amount'])
    
    # Convert to list and sort by month
    result = []
    for month_key in sorted(monthly_data.keys()):
        data = monthly_data[month_key]
        result.append({
            'month': data['month'],
            'total_spending': round(data['total_spending'], 2),
            'transaction_count': len(data['transactions']),
            'transactions': sorted(data['transactions'], key=lambda x: x['date'])
        })
    
    # Write to JSON file
    with open(output_file, 'w') as jsonfile:
        json.dump(result, jsonfile, indent=2)
    
    print(f"Conversion complete! JSON file saved to: {output_file}")
    print(f"\nSummary:")
    for month_data in result:
        print(f"{month_data['month']}: ${month_data['total_spending']:,.2f} ({month_data['transaction_count']} transactions)")

# Usage
if __name__ == "__main__":
    import os
    
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construct paths relative to script location
    input_path = os.path.join(script_dir, 'UserInputTest', 'accountactivity.csv')
    output_path = os.path.join(script_dir, '..', 'frontend', 'spending_by_month.json')
    
    convert_csv_to_json(input_path, output_path)