import pandas as pd
from prophet import Prophet
import json
from datetime import datetime, timedelta

class FinanceForecaster:
    """
    Handles financial forecasting using Prophet for the EarlyStart application.
    Takes pandas DataFrame from PDF extraction and generates 1-year projections.
    """
    def __init__(self):
        self.model = None
        
    def prepare_data(self, df, date_column='date', amount_column='amount'):
        """
        Convert DataFrame to Prophet format
        
        Args:
            df: pandas DataFrame with transactions
            date_column: name of date column (default: 'date')
            amount_column: name of spending column (default: 'amount')
            
        Returns:
            DataFrame ready for Prophet (ds, y columns)
        """
        # Aggregate by date to get daily spending
        daily_spending = df.groupby(date_column)[amount_column].sum().reset_index()
        
        # Rename to Prophet's required format
        prophet_df = pd.DataFrame({
            'ds': pd.to_datetime(daily_spending[date_column]),
            'y': daily_spending[amount_column]
        })
        
        # Sort by date
        prophet_df = prophet_df.sort_values('ds').reset_index(drop=True)
        
        return prophet_df
    
    def train_and_forecast(self, prophet_df, periods=365):
        """
        Train Prophet model and generate forecast
        
        Args:
            prophet_df: DataFrame with 'ds' and 'y' columns
            periods: number of days to forecast (default: 365 for 1 year)
            
        Returns:
            forecast DataFrame
        """
        # Initialize Prophet model
        self.model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,
            changepoint_prior_scale=0.05,
            interval_width=0.95
        )
        
        # Train the model
        self.model.fit(prophet_df)
        
        # Create future dates
        future = self.model.make_future_dataframe(periods=periods)
        
        # Make predictions
        forecast = self.model.predict(future)
        
        return forecast
    
    def generate_json_output(self, forecast, original_df=None, monthly_income=0):
        """
        Convert forecast to JSON for Flutter app
        
        Args:
            forecast: Prophet forecast DataFrame
            original_df: Original transaction data (optional)
            monthly_income: User's monthly income
            
        Returns:
            JSON string with all necessary data
        """
        # Get future predictions (not historical)
        future_predictions = forecast.tail(365)
        
        # Calculate statistics
        total_predicted_spending = future_predictions['yhat'].sum()
        annual_income = monthly_income * 12
        projected_savings = annual_income - total_predicted_spending
        
        # Prepare output
        output = {
            'forecast': {
                'dates': forecast['ds'].dt.strftime('%Y-%m-%d').tolist(),
                'predicted': forecast['yhat'].round(2).tolist(),
                'lower_bound': forecast['yhat_lower'].round(2).tolist(),
                'upper_bound': forecast['yhat_upper'].round(2).tolist()
            },
            'summary': {
                'total_predicted_spending_1yr': round(total_predicted_spending, 2),
                'annual_income': round(annual_income, 2),
                'projected_savings': round(projected_savings, 2),
                'savings_rate': round((projected_savings / annual_income * 100), 2) if annual_income > 0 else 0,
                'avg_daily_spending': round(future_predictions['yhat'].mean(), 2),
                'avg_monthly_spending': round(future_predictions['yhat'].mean() * 30, 2)
            },
            'metadata': {
                'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'forecast_days': len(future_predictions)
            }
        }
        
        # Add category breakdown if original data has categories
        if original_df is not None and 'category' in original_df.columns:
            category_spending = original_df.groupby('category')['amount'].agg(['sum', 'count']).round(2)
            output['categories'] = {
                cat: {
                    'total': float(row['sum']),
                    'count': int(row['count']),
                    'avg_per_transaction': round(row['sum'] / row['count'], 2)
                }
                for cat, row in category_spending.iterrows()
            }
        
        return json.dumps(output, indent=2)
    
    def process(self, df, monthly_income=0, date_column='date', amount_column='amount'):
        """
        Complete pipeline: DataFrame → Forecast → JSON
        
        Args:
            df: pandas DataFrame from partner's PDF extraction
            monthly_income: User's monthly income
            date_column: name of date column
            amount_column: name of amount column
            
        Returns:
            JSON string ready for Flutter app
        """
        # Step 1: Prepare data
        prophet_df = self.prepare_data(df, date_column, amount_column)
        
        # Step 2: Train and forecast
        forecast = self.train_and_forecast(prophet_df, periods=365)
        
        # Step 3: Generate JSON
        output_json = self.generate_json_output(forecast, df, monthly_income)
        
        return output_json


# Example usage
if __name__ == "__main__":
    # Example: Your partner gives you this DataFrame
    sample_data = pd.DataFrame({
        'date': pd.date_range('2024-01-01', periods=90, freq='D'),
        'amount': [45.50, 120.00, 23.75, 89.00, 15.50] * 18,
        'category': ['groceries', 'rent', 'transport', 'entertainment', 'food'] * 18
    })
    
    # Create forecaster
    forecaster = FinanceForecaster()
    
    # Process and get JSON
    result_json = forecaster.process(
        df=sample_data,
        monthly_income=3000,
        date_column='date',
        amount_column='amount'
    )
    
    print(result_json)
    
    # Save to file for Flutter to read
    with open('forecast_output.json', 'w') as f:
        f.write(result_json)
    
    print("\n✅ Forecast saved to forecast_output.json")