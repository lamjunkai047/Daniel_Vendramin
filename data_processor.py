"""
Data processing module for sales forecasting.
Handles Excel file reading and transformation to long format.
"""

import pandas as pd
import numpy as np
from typing import Tuple, Optional


def read_excel_file(file_path) -> pd.DataFrame:
    """
    Read the Excel file containing sales data.
    
    Args:
        file_path: Path to the Excel file or file-like object
        
    Returns:
        DataFrame with the raw data
    """
    # Handle both file paths and file-like objects (Streamlit uploads)
    try:
        if isinstance(file_path, str):
            return pd.read_excel(file_path, engine='openpyxl')
        else:
            # For Streamlit file uploader objects
            return pd.read_excel(file_path, engine='openpyxl')
    except Exception as e:
        # Try with xlrd engine for .xls files
        if hasattr(file_path, 'name') and file_path.name.endswith('.xls'):
            file_path.seek(0)  # Reset file pointer
            return pd.read_excel(file_path, engine='xlrd')
        else:
            raise e


def transform_to_long_format(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform the wide format data (months as columns) to long format.
    
    Args:
        df: DataFrame in wide format with months as columns
        
    Returns:
        DataFrame in long format with columns: Sales Force, Product PA, Key Figure, Date, Value
    """
    # Identify month columns (format: YY-MMM like '21-Jan', '22-Feb', etc.)
    month_columns = [col for col in df.columns if isinstance(col, str) and 
                     ('-' in col or col.replace('-', '').replace(' ', '').isdigit())]
    
    # If no month columns found, try to identify date-like columns
    if not month_columns:
        # Try to find columns that look like dates
        for col in df.columns:
            if isinstance(col, str):
                try:
                    pd.to_datetime(col, format='%y-%b', errors='raise')
                    month_columns.append(col)
                except:
                    pass
    
    # Columns to keep as identifiers
    id_columns = ['Sales Force', 'Product PA', 'Key Figure']
    
    # Filter to only keep columns that exist
    id_columns = [col for col in id_columns if col in df.columns]
    
    # Melt the dataframe
    long_df = pd.melt(
        df,
        id_vars=id_columns,
        value_vars=month_columns,
        var_name='Period',
        value_name='Value'
    )
    
    # Convert Period to datetime
    long_df['Period'] = pd.to_datetime(long_df['Period'], format='%y-%b', errors='coerce')
    
    # Remove rows with invalid dates or missing values
    long_df = long_df.dropna(subset=['Period'])
    
    return long_df


def extract_actuals_and_forecasts(df_long: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Extract actual sales and manual forecasts from the long format data.
    
    Args:
        df_long: DataFrame in long format
        
    Returns:
        Tuple of (actuals_df, forecasts_df)
        - actuals_df: Contains actual sales with columns: Sales Force, Product PA, Date, Actuals
        - forecasts_df: Contains manual forecasts with columns: Sales Force, Product PA, Date, Manual_Forecast
    """
    # Filter for Actuals Qty
    actuals = df_long[df_long['Key Figure'] == 'Actuals Qty'].copy()
    actuals_df = actuals[['Sales Force', 'Product PA', 'Period', 'Value']].copy()
    actuals_df.columns = ['Sales Force', 'Product PA', 'Date', 'Actuals']
    actuals_df = actuals_df.dropna(subset=['Actuals'])
    
    # Filter for Consensus Demand Final (manual forecasts)
    forecasts = df_long[df_long['Key Figure'] == 'Consensus Demand Final'].copy()
    forecasts_df = forecasts[['Sales Force', 'Product PA', 'Period', 'Value']].copy()
    forecasts_df.columns = ['Sales Force', 'Product PA', 'Date', 'Manual_Forecast']
    forecasts_df = forecasts_df.dropna(subset=['Manual_Forecast'])
    
    return actuals_df, forecasts_df


def prepare_prophet_data(actuals_df: pd.DataFrame, 
                        sales_force: Optional[str] = None,
                        product_pa: Optional[str] = None) -> pd.DataFrame:
    """
    Prepare data in Prophet format (ds: date, y: value).
    
    Args:
        actuals_df: DataFrame with actual sales
        sales_force: Optional filter for specific Sales Force
        product_pa: Optional filter for specific Product PA
        
    Returns:
        DataFrame with columns: ds (date), y (value)
    """
    # Filter if specific sales force or product is requested
    filtered_df = actuals_df.copy()
    
    if sales_force:
        filtered_df = filtered_df[filtered_df['Sales Force'] == sales_force]
    
    if product_pa:
        filtered_df = filtered_df[filtered_df['Product PA'] == product_pa]
    
    # Group by date and sum (in case of multiple products/sales forces)
    if sales_force and product_pa:
        # Single product, single sales force - just aggregate
        prophet_df = filtered_df.groupby('Date')['Actuals'].sum().reset_index()
    else:
        # Multiple products/sales forces - aggregate appropriately
        if sales_force:
            # Group by date and product
            prophet_df = filtered_df.groupby(['Date', 'Product PA'])['Actuals'].sum().reset_index()
        elif product_pa:
            # Group by date and sales force
            prophet_df = filtered_df.groupby(['Date', 'Sales Force'])['Actuals'].sum().reset_index()
        else:
            # Group by date only
            prophet_df = filtered_df.groupby('Date')['Actuals'].sum().reset_index()
    
    # Rename columns for Prophet
    if 'Date' in prophet_df.columns:
        prophet_df = prophet_df.rename(columns={'Date': 'ds', 'Actuals': 'y'})
    else:
        # If we have grouped by multiple columns, we need to handle differently
        # For now, let's assume we want to aggregate all
        prophet_df = filtered_df.groupby('Date')['Actuals'].sum().reset_index()
        prophet_df = prophet_df.rename(columns={'Date': 'ds', 'Actuals': 'y'})
    
    # Sort by date
    prophet_df = prophet_df.sort_values('ds').reset_index(drop=True)
    
    # Remove any negative or zero values (Prophet works better with positive values)
    prophet_df = prophet_df[prophet_df['y'] > 0]
    
    return prophet_df


def get_unique_combinations(actuals_df: pd.DataFrame) -> pd.DataFrame:
    """
    Get unique combinations of Sales Force and Product PA.
    
    Args:
        actuals_df: DataFrame with actual sales
        
    Returns:
        DataFrame with unique combinations
    """
    return actuals_df[['Sales Force', 'Product PA']].drop_duplicates().reset_index(drop=True)

