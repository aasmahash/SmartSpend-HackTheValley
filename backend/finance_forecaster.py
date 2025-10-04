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
        
    def prepare_data_for_prophet(self, df, date_column, value_column):
        """
        Convert pandas DataFrame to Prophet format
        
        Args:
            df: pandas DataFrame from PDF extraction
            date_column: name of your date column
            value_column: name of your spending/income column
        """
        # Create Prophet-compatible dataframe
        prophet_df = pd.DataFrame({
            'ds': pd.to_datetime(df[date_column]),
            'y': df[value_column]
        })
        
        # Sort by date
        prophet_df = prophet_df.sort_values('ds')
        
        return prophet_df
    
    def train_model(self, prophet_df):
        """Train Prophet model on historical data"""
        self.model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=False,
            daily_seasonality=False,
            changepoint_prior_scale=0.05  # Adjust for spending volatility
        )
        
        self.model.fit(prophet_df)
        return self.model
    
    def make_forecast(self, periods=365):
        """
        Generate future predictions
        
        Args:
            periods: number of days to forecast (365 for 1 year)
        """
        # Create future dataframe
        future = self.model.make_future_dataframe(periods=periods)
        
        # Make predictions
        forecast = self.model.predict(future)
        
        return forecast
    
    def get_forecast_json(self, forecast):
        """
        Convert forecast to JSON for Flutter app
        """
        result = {
            'dates': forecast['ds'].dt.strftime('%Y-%m-%d').tolist(),
            'predicted': forecast['yhat'].tolist(),
            'lower_bound': forecast['yhat_lower'].tolist(),
            'upper_bound': forecast['yhat_upper'].tolist()
        }
        
        return json.dumps(result)
  