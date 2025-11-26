"""
Prophet forecasting module for sales predictions.
Uses Meta's Prophet model to generate future sales forecasts.
"""

import pandas as pd
import numpy as np
from prophet import Prophet
from typing import Optional, Dict, Tuple
import warnings
warnings.filterwarnings('ignore')


def train_prophet_model(df: pd.DataFrame, 
                       periods: int = 12,
                       seasonality_mode: str = 'multiplicative',
                       yearly_seasonality: bool = True,
                       weekly_seasonality: bool = False,
                       daily_seasonality: bool = False,
                       changepoint_prior_scale: float = 0.05) -> Tuple[Prophet, pd.DataFrame]:
    """
    Train a Prophet model and generate forecasts.
    
    Args:
        df: DataFrame with columns 'ds' (date) and 'y' (value)
        periods: Number of future periods to forecast
        seasonality_mode: 'additive' or 'multiplicative'
        yearly_seasonality: Enable yearly seasonality
        weekly_seasonality: Enable weekly seasonality
        daily_seasonality: Enable daily seasonality
        changepoint_prior_scale: Flexibility of trend changes
        
    Returns:
        Tuple of (trained_model, forecast_dataframe)
    """
    # Ensure data is sorted by date
    df = df.sort_values('ds').reset_index(drop=True)
    
    # Initialize Prophet model
    model = Prophet(
        seasonality_mode=seasonality_mode,
        yearly_seasonality=yearly_seasonality,
        weekly_seasonality=weekly_seasonality,
        daily_seasonality=daily_seasonality,
        changepoint_prior_scale=changepoint_prior_scale,
        interval_width=0.95  # 95% confidence interval
    )
    
    # Fit the model
    model.fit(df)
    
    # Create future dataframe
    future = model.make_future_dataframe(periods=periods, freq='MS')  # MS = Month Start
    
    # Generate forecast
    forecast = model.predict(future)
    
    return model, forecast


def forecast_by_product(actuals_df: pd.DataFrame,
                        forecasts_df: pd.DataFrame,
                        periods: int = 12) -> pd.DataFrame:
    """
    Generate Prophet forecasts for each unique Sales Force and Product PA combination.
    
    Args:
        actuals_df: DataFrame with actual sales
        forecasts_df: DataFrame with manual forecasts (for comparison)
        periods: Number of future periods to forecast
        
    Returns:
        DataFrame with Prophet forecasts including comparison with manual forecasts
    """
    results = []
    
    # Get unique combinations
    combinations = actuals_df[['Sales Force', 'Product PA']].drop_duplicates()
    
    for idx, row in combinations.iterrows():
        sales_force = row['Sales Force']
        product_pa = row['Product PA']
        
        # Filter data for this combination
        product_actuals = actuals_df[
            (actuals_df['Sales Force'] == sales_force) & 
            (actuals_df['Product PA'] == product_pa)
        ].copy()
        
        if len(product_actuals) < 3:  # Need at least 3 data points
            continue
        
        # Prepare Prophet data
        prophet_data = product_actuals[['Date', 'Actuals']].copy()
        prophet_data.columns = ['ds', 'y']
        prophet_data = prophet_data.sort_values('ds').reset_index(drop=True)
        prophet_data = prophet_data[prophet_data['y'] > 0]  # Remove zeros/negatives
        
        if len(prophet_data) < 3:
            continue
        
        try:
            # Train model and forecast
            model, forecast = train_prophet_model(prophet_data, periods=periods)
            
            # Extract future forecasts only
            future_forecast = forecast.tail(periods).copy()
            future_forecast['Sales Force'] = sales_force
            future_forecast['Product PA'] = product_pa
            
            # Get manual forecasts for comparison
            product_manual = forecasts_df[
                (forecasts_df['Sales Force'] == sales_force) & 
                (forecasts_df['Product PA'] == product_pa)
            ].copy()
            
            # Normalize dates to month start for merging
            future_forecast['ds'] = pd.to_datetime(future_forecast['ds']).dt.to_period('M').dt.to_timestamp()
            product_manual['Date'] = pd.to_datetime(product_manual['Date']).dt.to_period('M').dt.to_timestamp()
            
            # Merge with manual forecasts
            future_forecast = future_forecast.merge(
                product_manual[['Date', 'Manual_Forecast']],
                left_on='ds',
                right_on='Date',
                how='left'
            )
            
            # Select relevant columns
            result = future_forecast[[
                'Sales Force', 'Product PA', 'ds', 'yhat', 'yhat_lower', 'yhat_upper', 'Manual_Forecast'
            ]].copy()
            result.columns = [
                'Sales Force', 'Product PA', 'Date', 'Prophet_Forecast', 
                'Prophet_Lower', 'Prophet_Upper', 'Manual_Forecast'
            ]
            
            results.append(result)
            
        except Exception as e:
            print(f"Error forecasting for {sales_force} - {product_pa}: {str(e)}")
            continue
    
    if results:
        return pd.concat(results, ignore_index=True)
    else:
        return pd.DataFrame()


def calculate_accuracy_metrics(actuals: pd.Series, 
                              forecasts: pd.Series) -> Dict[str, float]:
    """
    Calculate forecast accuracy metrics: MAPE, WMAPE, Bias, RMSE.
    
    Args:
        actuals: Series of actual values
        forecasts: Series of forecasted values
        
    Returns:
        Dictionary with accuracy metrics
    """
    # Remove NaN values
    mask = ~(pd.isna(actuals) | pd.isna(forecasts))
    actuals_clean = actuals[mask]
    forecasts_clean = forecasts[mask]
    
    if len(actuals_clean) == 0:
        return {
            'MAPE': np.nan,
            'WMAPE': np.nan,
            'Bias': np.nan,
            'RMSE': np.nan
        }
    
    # Calculate errors
    errors = actuals_clean - forecasts_clean
    abs_errors = np.abs(errors)
    pct_errors = abs_errors / (actuals_clean + 1e-10)  # Add small value to avoid division by zero
    
    # MAPE (Mean Absolute Percentage Error)
    mape = np.mean(pct_errors) * 100
    
    # WMAPE (Weighted Mean Absolute Percentage Error)
    total_actuals = np.sum(actuals_clean)
    if total_actuals > 0:
        wmape = np.sum(abs_errors) / total_actuals * 100
    else:
        wmape = np.nan
    
    # Bias (Mean Error)
    bias = np.mean(errors)
    
    # RMSE (Root Mean Squared Error)
    rmse = np.sqrt(np.mean(errors ** 2))
    
    return {
        'MAPE': mape,
        'WMAPE': wmape,
        'Bias': bias,
        'RMSE': rmse
    }

