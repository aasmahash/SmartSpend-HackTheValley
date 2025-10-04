import pandas as pd
from prophet import Prophet
import json
from datetime import datetime, timedelta

class FinanceForecaster:
    """
    Handles financial forecasting using Prophet for the EarlyStart application.
    Takes pandas DataFrame from PDF extraction and generates 1-year projections.
    """
    
  