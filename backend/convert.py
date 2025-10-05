"""
Updated convert.py to save outputs to Flutter frontend folder
"""
import os
import pandas as pd
from visualize import main
import json
import shutil
import subprocess
import platform


def load_and_process_csv(csv_path):
    """
    Load CSV in new format and convert to standard format
    """
    print("=" * 60)
    print("LOADING NEW CSV FORMAT")
    print("=" * 60)
    
    df = pd.read_csv(csv_path)
    
    print(f"\n📋 CSV Structure Detected:")
    print(f"  Columns found: {list(df.columns)}")
    print(f"  Total rows: {len(df)}")
    
    # Identify columns
    date_col = None
    for col in df.columns:
        if 'date' in col.lower() or df[col].dtype == 'object':
            try:
                pd.to_datetime(df[col])
                date_col = col
                break
            except:
                continue
    
    if date_col is None:
        date_col = df.columns[0]
    
    amount_col = None
    for col in df.columns:
        if 'amount' in col.lower() or pd.api.types.is_numeric_dtype(df[col]):
            if df[col].notna().any() and (df[col] > 0).any():
                amount_col = col
                break
    
    if amount_col is None:
        for col in df.columns:
            try:
                numeric_vals = pd.to_numeric(df[col], errors='coerce')
                if numeric_vals.notna().any():
                    amount_col = col
                    break
            except:
                continue
    
    description_col = None
    for col in df.columns:
        if col != date_col and col != amount_col:
            if df[col].dtype == 'object':
                description_col = col
                break
    
    if description_col is None:
        description_col = df.columns[1] if len(df.columns) > 1 else None
    
    print(f"\n🔍 Identified Columns:")
    print(f"  Date: {date_col}")
    print(f"  Description: {description_col}")
    print(f"  Amount: {amount_col}")
    
    # Create standardized DataFrame
    processed_df = pd.DataFrame()
    processed_df['date'] = pd.to_datetime(df[date_col])
    processed_df['amount'] = pd.to_numeric(df[amount_col], errors='coerce').abs()
    
    if description_col:
        processed_df['category'] = df[description_col].fillna('other')
    else:
        processed_df['category'] = 'other'
    
    # Clean data
    processed_df = processed_df.dropna(subset=['amount'])
    processed_df = processed_df[processed_df['amount'] > 0]
    processed_df = processed_df[~processed_df['category'].str.contains('PAYMENT', case=False, na=False)]
    
    print(f"\n✓ Data Processing Complete:")
    print(f"  Valid transactions: {len(processed_df)}")
    print(f"  Date range: {processed_df['date'].min()} to {processed_df['date'].max()}")
    print(f"  Total spending: ${processed_df['amount'].sum():,.2f}")
    
    print(f"\n📊 Category Breakdown:")
    category_summary = processed_df.groupby('category')['amount'].agg(['sum', 'count'])
    for cat, row in category_summary.iterrows():
        print(f"  {cat}: ${row['sum']:,.2f} ({row['count']} transactions)")
    
    return processed_df[['date', 'amount', 'category']]


def get_flutter_assets_path(script_dir):
    """
    Get the Flutter frontend folder (no assets subfolder)
    """
    # Go up from backend to project root, then into frontend
    frontend_dir = os.path.join(script_dir, '..', 'frontend')
    
    # Create frontend folder if it doesn't exist
    os.makedirs(frontend_dir, exist_ok=True)
    
    return frontend_dir


def main_pipeline(csv_path, monthly_income=3500):
    """
    Complete pipeline that saves to Flutter assets folder
    """
    # Load and process the CSV
    df = load_and_process_csv(csv_path)
    
    print("\n" + "=" * 60)
    print("PROCESSED DATA PREVIEW")
    print("=" * 60)
    print(df.head(10))
    
    print("\n" + "=" * 60)
    print("RUNNING FORECAST PIPELINE")
    print("=" * 60)
    
    # Run forecasting using visualize.py (creates the fancy graph!)
    forecast_df = df[['date', 'amount', 'category']]
    results = main(forecast_df, monthly_income=monthly_income)
    
    # Get paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    flutter_assets = get_flutter_assets_path(script_dir)
    
    print("\n" + "=" * 60)
    print("COPYING FILES TO FLUTTER FRONTEND")
    print("=" * 60)
    
    # Copy JSON from backend to frontend
    json_source = os.path.join(script_dir, 'forecast_output.json')
    json_dest = os.path.join(flutter_assets, 'forecast_output.json')
    if os.path.exists(json_source):
        shutil.copy2(json_source, json_dest)
        print(f"✓ JSON copied to: {json_dest}")
    
    # Copy PNG from backend to frontend
    png_source = os.path.join(script_dir, 'forecast_plot.png')
    png_dest = os.path.join(flutter_assets, 'forecast_plot.png')
    if os.path.exists(png_source):
        shutil.copy2(png_source, png_dest)
        print(f"✓ PNG copied to: {png_dest}")
    
        # Open the image automatically
        try:
            if platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', png_dest])
            elif platform.system() == 'Windows':
                os.startfile(png_dest)
            else:  # Linux
                subprocess.run(['xdg-open', png_dest])
        except:
            pass
    
    print("\n" + "=" * 60)
    print("✅ PROCESSING COMPLETE!")
    print("=" * 60)
    print(f"\nFlutter Frontend Location: {flutter_assets}")
    print("\n📱 Files ready for Flutter:")
    print("  ✓ forecast_output.json")
    print("  ✓ forecast_plot.png")
    
    print("\n💡 Next Steps:")
    print("  1. Load JSON in Flutter:")
    print("     final file = File('forecast_output.json');")
    print("     final jsonString = await file.readAsString();")
    print("\n  2. Display image:")
    print("     Image.file(File('forecast_plot.png'))")
    
    return results


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    csv_filename = 'accountactivity.csv'
    csv_path = os.path.join(script_dir, 'UserInputTest', csv_filename)
    
    print("🚀 SMARTSPEND FINANCIAL FORECASTER")
    print(f"📁 Loading: {csv_filename}\n")
    
    if not os.path.exists(csv_path):
        print(f"❌ Error: CSV file not found at {csv_path}")
        print("\n💡 Please update 'csv_filename' in the script to match your file name")
        
        test_dir = os.path.join(script_dir, 'UserInputTest')
        if os.path.exists(test_dir):
            files = [f for f in os.listdir(test_dir) if f.endswith('.csv')]
            if files:
                print(f"\n   CSV files found in UserInputTest/:")
                for f in files:
                    print(f"     - {f}")
    else:
        results = main_pipeline(csv_path, monthly_income=3500)