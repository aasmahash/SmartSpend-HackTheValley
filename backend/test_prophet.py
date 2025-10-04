"""
test_prophet.py
Test the finance forecaster with realistic student spending data
"""

import pandas as pd
import numpy as np
from finance_forecaster import FinanceForecaster
import json

# Set random seed for reproducibility
np.random.seed(42)

# Create realistic student spending data (3 months of history)
def generate_student_spending():
    """Generate realistic student spending patterns"""
    dates = pd.date_range('2024-07-01', periods=90, freq='D')
    
    spending_data = []
    
    for date in dates:
        # Simulate different spending patterns
        day_of_week = date.dayofweek
        
        # Weekend spending is higher
        if day_of_week >= 5:  # Saturday/Sunday
            daily_spending = np.random.uniform(40, 120)
        else:  # Weekdays
            daily_spending = np.random.uniform(20, 80)
        
        # Add some monthly expenses (rent on 1st of month)
        if date.day == 1:
            daily_spending += 1200  # Rent
        
        # Add some variation
        category_weights = {
            'groceries': 0.3,
            'food': 0.25,
            'transport': 0.15,
            'entertainment': 0.2,
            'utilities': 0.1
        }
        
        category = np.random.choice(
            list(category_weights.keys()),
            p=list(category_weights.values())
        )
        
        spending_data.append({
            'date': date,
            'amount': round(daily_spending, 2),
            'category': category,
            'description': f'{category.title()} expense'
        })
    
    return pd.DataFrame(spending_data)

# Generate test data
print("📊 Generating test spending data...")
test_df = generate_student_spending()

print(f"✅ Generated {len(test_df)} transactions")
print(f"\n📈 Sample data:")
print(test_df.head(10))

print(f"\n💰 Total spending in data: ${test_df['amount'].sum():.2f}")
print(f"📅 Date range: {test_df['date'].min()} to {test_df['date'].max()}")

# Test the forecaster
print("\n🔮 Running Prophet forecaster...")
forecaster = FinanceForecaster()

monthly_income = 3500  # Student income (e.g., from part-time job + parents)

result_json = forecaster.process(
    df=test_df,
    monthly_income=monthly_income,
    date_column='date',
    amount_column='amount'
)

# Parse the JSON to display nicely
result = json.loads(result_json)

print("\n" + "="*60)
print("📊 FORECAST SUMMARY")
print("="*60)

summary = result['summary']
print(f"\n💸 Predicted Annual Spending: ${summary['total_predicted_spending_1yr']:,.2f}")
print(f"💰 Annual Income: ${summary['annual_income']:,.2f}")
print(f"💵 Projected Savings: ${summary['projected_savings']:,.2f}")
print(f"📈 Savings Rate: {summary['savings_rate']:.2f}%")
print(f"\n📊 Average Daily Spending: ${summary['avg_daily_spending']:.2f}")
print(f"📊 Average Monthly Spending: ${summary['avg_monthly_spending']:.2f}")

if 'categories' in result:
    print("\n" + "="*60)
    print("🏷️  SPENDING BY CATEGORY")
    print("="*60)
    
    for category, data in sorted(
        result['categories'].items(),
        key=lambda x: x[1]['total'],
        reverse=True
    ):
        print(f"\n{category.upper()}")
        print(f"  Total: ${data['total']:,.2f}")
        print(f"  Transactions: {data['count']}")
        print(f"  Avg per transaction: ${data['avg_per_transaction']:.2f}")

# Save to file
output_file = 'forecast_output.json'
with open(output_file, 'w') as f:
    f.write(result_json)

print("\n" + "="*60)
print(f"✅ Full forecast saved to: {output_file}")
print("="*60)

# Show what-if scenario
print("\n💡 WHAT-IF SCENARIO")
print("="*60)
if 'categories' in result:
    # Find highest spending category
    highest_category = max(result['categories'].items(), key=lambda x: x[1]['total'])
    category_name = highest_category[0]
    category_total = highest_category[1]['total']
    
    # Calculate 50% reduction
    reduction = category_total * 0.5
    annual_reduction = reduction * (365 / 90)  # Project to full year
    
    print(f"If you reduce '{category_name}' spending by 50%:")
    print(f"  Current annual projection: ${category_total * (365/90):,.2f}")
    print(f"  After 50% reduction: ${category_total * (365/90) * 0.5:,.2f}")
    print(f"  💰 Annual savings: ${annual_reduction:,.2f}")
    print(f"  📈 New savings rate: {((summary['projected_savings'] + annual_reduction) / summary['annual_income'] * 100):.2f}%")

print("\n🎉 Test complete! Ready for Flutter integration.")