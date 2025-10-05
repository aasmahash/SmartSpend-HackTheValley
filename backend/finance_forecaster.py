import pandas as pd
from prophet import Prophet
import json
from datetime import datetime
import numpy as np

class FinanceForecaster:
    """
    Improved forecaster for transaction data with better handling of sparse patterns
    """
    def __init__(self):
        self.model = None
        
    def prepare_data(self, df, date_column='date', amount_column='amount'):
        """
        Prepare daily transaction data with proper aggregation
        """
        df_copy = df.copy()
        df_copy[date_column] = pd.to_datetime(df_copy[date_column])
        
        # Remove duplicates first
        df_copy = df_copy.drop_duplicates(subset=[date_column, amount_column])
        
        # Filter out payment entries (they're not spending)
        if 'category' in df_copy.columns:
            df_copy = df_copy[~df_copy['category'].str.contains('PAYMENT', case=False, na=False)]
        
        # Aggregate by day
        daily_spending = df_copy.groupby(date_column)[amount_column].sum().reset_index()
        
        # Create Prophet format
        prophet_df = pd.DataFrame({
            'ds': daily_spending[date_column],
            'y': daily_spending[amount_column]
        })
        
        # Fill missing days with zero (important for Prophet to understand spending patterns)
        date_range = pd.date_range(
            start=prophet_df['ds'].min(),
            end=prophet_df['ds'].max(),
            freq='D'
        )
        complete_df = pd.DataFrame({'ds': date_range})
        prophet_df = complete_df.merge(prophet_df, on='ds', how='left')
        prophet_df['y'] = prophet_df['y'].fillna(0)
        
        return prophet_df
    
    def train_and_forecast(self, prophet_df, periods=365):
        """
        Train model with improved settings for spending data
        """
        # Calculate statistics for reasonable bounds
        daily_avg = prophet_df[prophet_df['y'] > 0]['y'].mean()
        daily_std = prophet_df[prophet_df['y'] > 0]['y'].std()
        
        print(f"\n📊 Historical Statistics:")
        print(f"  Average daily spending: ${daily_avg:.2f}")
        print(f"  Std deviation: ${daily_std:.2f}")
        print(f"  Days with transactions: {(prophet_df['y'] > 0).sum()}")
        print(f"  Total days: {len(prophet_df)}")
        
        # More flexible model for spending patterns
        self.model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,
            changepoint_prior_scale=0.8,  # Very flexible for limited data
            seasonality_prior_scale=15,   # Strong seasonality
            seasonality_mode='multiplicative',  # Better for spending patterns
            interval_width=0.80,
            changepoint_range=0.95  # Allow changes throughout entire history
        )
        
        # Add monthly seasonality
        self.model.add_seasonality(name='monthly', period=30.5, fourier_order=5)
        
        # Fit model
        print("\n🔄 Training Prophet model...")
        self.model.fit(prophet_df)
        
        # Forecast
        future = self.model.make_future_dataframe(periods=periods, freq='D')
        forecast = self.model.predict(future)
        
        # Apply reasonable bounds
        forecast['yhat'] = forecast['yhat'].clip(lower=0)
        forecast['yhat_lower'] = forecast['yhat_lower'].clip(lower=0)
        
        # Cap at 5x historical daily average (prevent extreme predictions)
        max_daily = daily_avg * 5
        forecast['yhat'] = forecast['yhat'].clip(upper=max_daily)
        forecast['yhat_upper'] = forecast['yhat_upper'].clip(upper=max_daily * 1.5)
        
        return forecast
    
    def generate_json_output(self, forecast, original_df=None, monthly_income=0):
        """
        Generate monthly forecast summary
        """
        # Get future predictions (next 365 days)
        future_predictions = forecast[forecast['ds'] > forecast['ds'].max() - pd.Timedelta(days=365)]
        
        # Convert to monthly
        future_predictions = future_predictions.copy()
        future_predictions['month'] = pd.to_datetime(future_predictions['ds']).dt.to_period('M')
        monthly_forecast = future_predictions.groupby('month').agg({
            'yhat': 'sum',
            'yhat_lower': 'sum',
            'yhat_upper': 'sum'
        }).reset_index()
        monthly_forecast['month'] = monthly_forecast['month'].dt.to_timestamp()
        
        # Get only next 12 months
        monthly_forecast = monthly_forecast.head(12)
        
        total_predicted_spending = monthly_forecast['yhat'].sum()
        avg_monthly_spending = monthly_forecast['yhat'].mean()
        
        annual_income = monthly_income * 12
        projected_savings = annual_income - total_predicted_spending
        
        output = {
            'forecast': {
                'dates': monthly_forecast['month'].dt.strftime('%Y-%m-%d').tolist(),
                'predicted': monthly_forecast['yhat'].round(2).tolist(),
                'lower_bound': monthly_forecast['yhat_lower'].round(2).tolist(),
                'upper_bound': monthly_forecast['yhat_upper'].round(2).tolist()
            },
            'summary': {
                'total_predicted_spending_1yr': round(total_predicted_spending, 2),
                'annual_income': round(annual_income, 2),
                'projected_savings': round(projected_savings, 2),
                'savings_rate': round((projected_savings / annual_income * 100), 2) if annual_income > 0 else 0,
                'avg_monthly_spending': round(avg_monthly_spending, 2)
            },
            'metadata': {
                'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'forecast_months': 12,
                'data_aggregation': 'daily_to_monthly'
            }
        }
        
        if original_df is not None and 'category' in original_df.columns:
            # Remove payment entries from category analysis
            spending_df = original_df[~original_df['category'].str.contains('PAYMENT', case=False, na=False)]
            category_spending = spending_df.groupby('category')['amount'].agg(['sum', 'count']).round(2)
            output['categories'] = {
                cat: {
                    'total': float(row['sum']),
                    'count': int(row['count']),
                    'avg_per_transaction': round(row['sum'] / row['count'], 2)
                }
                for cat, row in category_spending.iterrows()
            }
        
        return json.dumps(output, indent=2)
    
    def process(self, df, monthly_income=0, date_column='date', amount_column='amount', output_dir=None):
        """
        Complete pipeline with configurable output directory
        """
        print("\n" + "="*60)
        print("PROCESSING TRANSACTION DATA")
        print("="*60)
        
        # Clean data
        df_clean = df.copy()
        df_clean = df_clean.drop_duplicates()
        if 'category' in df_clean.columns:
            df_clean = df_clean[~df_clean['category'].str.contains('PAYMENT', case=False, na=False)]
        
        print(f"\nCleaned data:")
        print(f"  Total transactions: {len(df_clean)}")
        print(f"  Date range: {df_clean[date_column].min()} to {df_clean[date_column].max()}")
        print(f"  Total spending: ${df_clean[amount_column].sum():.2f}")
        
        prophet_df = self.prepare_data(df_clean, date_column, amount_column)
        forecast = self.train_and_forecast(prophet_df, periods=365)
        output_json = self.generate_json_output(forecast, df_clean, monthly_income)
        
        return output_json, forecast, prophet_df


# Example usage
if __name__ == "__main__":
    # Load your data
    df = pd.read_csv('accountactivity.csv')
    
    # Identify columns (adjust these based on your CSV structure)
    df.columns = ['date', 'category', 'amount', 'balance']  # Update as needed
    
    # Process
    forecaster = FinanceForecaster()
    json_output, forecast, prophet_df = forecaster.process(
        df[['date', 'amount', 'category']], 
        monthly_income=3500
    )
    
    print("\n" + "="*60)
    print("FORECAST RESULTS")
    print("="*60)
    print(json_output)