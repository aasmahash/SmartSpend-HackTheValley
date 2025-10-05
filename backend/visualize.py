"""
integrate_and_visualize.py
Complete integration: Partner's PDF data → Prophet → Visualization + JSON

This combines:
1. Your DataFrame input
2. Your finance_forecaster.py processing
3. Graph visualization (like your test_prophet.py)
4. JSON output for Flutter
"""

import pandas as pd
import matplotlib.pyplot as plt
from finance_forecaster import FinanceForecaster
import json
from datetime import datetime
import os

def visualize_forecast(original_df, forecast_df, monthly_income, output_path='forecast_plot.png'):
    """
    Create visualization similar to your test_prophet.py
    
    Args:
        original_df: Original transaction data (with date, amount columns)
        forecast_df: Prophet forecast DataFrame
        monthly_income: User's monthly income
        output_path: Where to save the plot
    """
    print("\n" + "=" * 60)
    print("CREATING VISUALIZATION")
    print("=" * 60)
    
    try:
        # Aggregate original data by month for cleaner visualization
        original_df['date'] = pd.to_datetime(original_df['date'])
        monthly_historical = original_df.groupby(
            original_df['date'].dt.to_period('M')
        )['amount'].sum().reset_index()
        monthly_historical['date'] = monthly_historical['date'].dt.to_timestamp()
        
        # Get future predictions (next 12 months from last data point)
        last_historical_date = original_df['date'].max()
        future_data = forecast_df[forecast_df['ds'] > last_historical_date].head(52)
        
        # Aggregate forecast by month
        future_data['month'] = pd.to_datetime(future_data['ds']).dt.to_period('M')
        monthly_forecast = future_data.groupby('month').agg({
            'yhat': 'sum',
            'yhat_lower': 'sum',
            'yhat_upper': 'sum'
        }).reset_index()
        monthly_forecast['month'] = monthly_forecast['month'].dt.to_timestamp()
        
        # Create the plot
        fig, ax = plt.subplots(figsize=(14, 7))
        
        # Plot historical spending
        ax.plot(monthly_historical['date'], monthly_historical['amount'], 
                'ko-', label='Historical Spending', linewidth=2.5, markersize=10)
        
        # Plot forecast
        ax.plot(monthly_forecast['month'], monthly_forecast['yhat'], 
                'b--', label='Predicted Spending', linewidth=2.5)
        
        # Add uncertainty band
        ax.fill_between(monthly_forecast['month'], 
                         monthly_forecast['yhat_lower'], 
                         monthly_forecast['yhat_upper'],
                         alpha=0.3, color='blue', label='Uncertainty Range')
        
        # Add income reference line (monthly)
        ax.axhline(y=monthly_income, color='green', 
                   linestyle='-.', linewidth=2, label=f'Monthly Income (${monthly_income:,.0f})')
        
        # Add vertical line for "today"
        ax.axvline(x=last_historical_date, color='red', 
                   linestyle=':', linewidth=2.5, label='Today')
        
        # Labels and formatting
        ax.set_xlabel('Date', fontsize=13, fontweight='bold')
        ax.set_ylabel('Monthly Spending ($)', fontsize=13, fontweight='bold')
        ax.set_title('EarlyStart: Your 12-Month Spending Forecast', 
                     fontsize=16, fontweight='bold', pad=20)
        ax.legend(loc='best', fontsize=11)
        ax.grid(True, alpha=0.3, linestyle='--')
        
        # Format y-axis as currency
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        # Rotate x-axis labels
        plt.xticks(rotation=45, ha='right')
        
        plt.tight_layout()
        
        # Save the plot
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Graph saved as '{output_path}'")
        
        # Display the plot
        plt.show()
        
        return True
        
    except Exception as e:
        print(f"⚠️  Could not create visualization: {e}")
        return False


def main(df, monthly_income=3500):
    """
    Main integration function
    
    Args:
        df: DataFrame from your partner's PDF extraction
            Must have columns: 'date', 'amount', (optional: 'category')
        monthly_income: User's monthly income
    
    Returns:
        dict with JSON output and forecast data
    """
    
    print("=" * 60)
    print("EARLYSTART FINANCE FORECASTER")
    print("=" * 60)
    
    # Display input data summary
    print(f"\n📊 Input Data Summary:")
    print(f"  Transactions: {len(df)}")
    print(f"  Date Range: {df['date'].min()} to {df['date'].max()}")
    print(f"  Total Spending: ${df['amount'].sum():,.2f}")
    print(f"  Monthly Income: ${monthly_income:,.2f}")
    
    if 'category' in df.columns:
        print(f"\n🏷️  Categories found: {df['category'].nunique()}")
        print(f"  Top category: {df.groupby('category')['amount'].sum().idxmax()}")
    
    # Run Prophet forecasting
    print("\n" + "=" * 60)
    print("RUNNING PROPHET FORECAST")
    print("=" * 60)
    
    forecaster = FinanceForecaster()
    
    # Get the internal Prophet forecast for visualization
    prophet_df = forecaster.prepare_data(df, 'date', 'amount')
    forecast_df = forecaster.train_and_forecast(prophet_df, periods=52)
    
    # Generate JSON output for Flutter
    result_json = forecaster.generate_json_output(forecast_df, df, monthly_income)
    result = json.loads(result_json)
    
    print("✓ Forecast generated successfully!")
    
    # Display summary
    print("\n" + "=" * 60)
    print("FORECAST SUMMARY")
    print("=" * 60)
    
    summary = result['summary']
    print(f"\n💸 Predicted Annual Spending: ${summary['total_predicted_spending_1yr']:,.2f}")
    print(f"💰 Annual Income: ${summary['annual_income']:,.2f}")
    print(f"💵 Projected Savings: ${summary['projected_savings']:,.2f}")
    print(f"📈 Savings Rate: {summary['savings_rate']:.2f}%")
    print(f"\n📊 Average Monthly Spending: ${summary['avg_monthly_spending']:.2f}")
    
    # Savings status
    if summary['projected_savings'] > 0:
        print("\n✓ Great! You're on track to save money!")
    else:
        overspend = abs(summary['projected_savings'])
        print(f"\n⚠️  Warning: You may overspend by ${overspend:,.2f}")
        print("💡 Consider reducing expenses!")
    
    # Category breakdown
    if 'categories' in result:
        print("\n" + "=" * 60)
        print("SPENDING BY CATEGORY")
        print("=" * 60)
        
        for category, data in sorted(
            result['categories'].items(),
            key=lambda x: x[1]['total'],
            reverse=True
        ):
            percentage = (data['total'] / df['amount'].sum()) * 100
            print(f"\n{category.upper()}")
            print(f"  Total: ${data['total']:,.2f} ({percentage:.1f}%)")
            print(f"  Avg per transaction: ${data['avg_per_transaction']:.2f}")
    
    # GET PATH TO FRONTEND FOLDER
    script_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(script_dir, '..', 'frontend')
    
    # Create frontend folder if it doesn't exist
    os.makedirs(frontend_dir, exist_ok=True)
    
    # Create visualization and save to frontend
    plot_path = os.path.join(frontend_dir, 'forecast_plot.png')
    visualize_forecast(df, forecast_df, monthly_income, output_path=plot_path)
    
    # Save JSON to frontend
    json_path = os.path.join(frontend_dir, 'forecast_output.json')
    with open(json_path, 'w') as f:
        f.write(result_json)
    
    print("\n" + "=" * 60)
    print("✓ FILES SAVED TO FRONTEND FOLDER")
    print("=" * 60)
    print(f"  - {json_path}")
    print(f"  - {plot_path}")
    print("\nReady for Flutter integration! 🚀")
    
    return {
        'json': result_json,
        'forecast': forecast_df,
        'summary': summary
    }


# ============================================
# USAGE EXAMPLES
# ============================================

if __name__ == "__main__":
    
    print("\n🔧 TESTING WITH SAMPLE DATA")
    print("(Replace this with your partner's DataFrame)\n")
    
    # Example 1: Simulate partner's DataFrame
    import numpy as np
    np.random.seed(42)
    
    # Create realistic test data (3 months)
    dates = pd.date_range('2024-07-01', periods=90, freq='D')
    sample_df = pd.DataFrame({
        'date': dates,
        'amount': np.random.uniform(20, 150, 90),
        'category': np.random.choice(
            ['groceries', 'rent', 'transport', 'entertainment', 'food'], 
            90
        )
    })
    
    # Add some big expenses (rent)
    for i in range(0, 90, 30):
        sample_df.loc[i, 'amount'] = 1200
        sample_df.loc[i, 'category'] = 'rent'
    
    # Run the full pipeline
    results = main(sample_df, monthly_income=3500)
    
    print("\n" + "=" * 60)
    print("✓ TEST COMPLETE!")
    print("=" * 60)
    print("\nNow you can integrate with your partner's code:")
    print("\n  # Import their PDF extractor")
    print("  from partner_code import extract_pdf_to_dataframe")
    print("\n  # Get their DataFrame")
    print("  df = extract_pdf_to_dataframe('statement.pdf')")
    print("\n  # Run your forecaster")
    print("  results = main(df, monthly_income=3500)")
    print("\n  # Done! Graph + JSON generated")
    print("=" * 60)