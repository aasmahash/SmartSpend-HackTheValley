"""
Test the complete pipeline with a CSV file
"""
import os 
import pandas as pd
from visualize import main

script_dir = os.path.dirname(os.path.abspath(__file__))
# Load the test CSV
print("Loading test data from CSV...")
# Build the full path to the CSV
csv_path = os.path.join(script_dir, 'UserInputTest', 'testspending.csv')

print(f"Looking for CSV at: {csv_path}")  # Optional: shows where it's looking
df = pd.read_csv(csv_path)


# Display the data
print("\nTest Data Preview:")
print(df.head(10))
print(f"\nTotal rows: {len(df)}")
print(f"Date range: {df['date'].min()} to {df['date'].max()}")
print(f"Total spending: ${df['amount'].sum():.2f}")

# Run the complete pipeline (forecast + visualization + JSON)
print("\n" + "="*60)
print("RUNNING COMPLETE PIPELINE...")
print("="*60 + "\n")

results = main(df, monthly_income=3500)

print("\n✅ Test completed successfully!")
print("Check for these outputs:")
print("  - forecast_plot.png (the graph)")
print("  - forecast_output.json (the JSON data)")