"""
Forecast comparison module.
Compares Prophet forecasts with manual forecasts and calculates accuracy metrics.
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple
from prophet_forecaster import calculate_accuracy_metrics


def compare_forecasts(prophet_forecasts: pd.DataFrame,
                     actuals_df: pd.DataFrame,
                     manual_forecasts_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compare Prophet forecasts with manual forecasts and actuals.
    
    Args:
        prophet_forecasts: DataFrame with Prophet forecasts
        actuals_df: DataFrame with actual sales
        manual_forecasts_df: DataFrame with manual forecasts
        
    Returns:
        DataFrame with comparison metrics
    """
    comparison_results = []
    
    # Get unique combinations
    combinations = prophet_forecasts[['Sales Force', 'Product PA']].drop_duplicates()
    
    for idx, row in combinations.iterrows():
        sales_force = row['Sales Force']
        product_pa = row['Product PA']
        
        # Get Prophet forecasts for this combination
        prophet_data = prophet_forecasts[
            (prophet_forecasts['Sales Force'] == sales_force) & 
            (prophet_forecasts['Product PA'] == product_pa)
        ].copy()
        
        # Get actuals for this combination
        actuals_data = actuals_df[
            (actuals_df['Sales Force'] == sales_force) & 
            (actuals_df['Product PA'] == product_pa)
        ].copy()
        
        # Get manual forecasts for this combination
        manual_data = manual_forecasts_df[
            (manual_forecasts_df['Sales Force'] == sales_force) & 
            (manual_forecasts_df['Product PA'] == product_pa)
        ].copy()
        
        # Normalize dates to month start for consistent merging
        prophet_data['Date'] = pd.to_datetime(prophet_data['Date']).dt.to_period('M').dt.to_timestamp()
        actuals_data['Date'] = pd.to_datetime(actuals_data['Date']).dt.to_period('M').dt.to_timestamp()
        manual_data['Date'] = pd.to_datetime(manual_data['Date']).dt.to_period('M').dt.to_timestamp()
        
        # Merge on date for comparison
        comparison_df = prophet_data.merge(
            actuals_data[['Date', 'Actuals']],
            on='Date',
            how='left'
        ).merge(
            manual_data[['Date', 'Manual_Forecast']],
            on='Date',
            how='left'
        )
        
        # Calculate metrics where we have actuals (historical comparison)
        historical = comparison_df[comparison_df['Actuals'].notna()].copy()
        
        if len(historical) > 0:
            # Prophet accuracy
            prophet_metrics = calculate_accuracy_metrics(
                historical['Actuals'],
                historical['Prophet_Forecast']
            )
            
            # Manual forecast accuracy
            manual_metrics = calculate_accuracy_metrics(
                historical['Actuals'],
                historical['Manual_Forecast']
            )
            
            # Add to results
            result = {
                'Sales Force': sales_force,
                'Product PA': product_pa,
                'Prophet_MAPE': prophet_metrics['MAPE'],
                'Prophet_WMAPE': prophet_metrics['WMAPE'],
                'Prophet_Bias': prophet_metrics['Bias'],
                'Prophet_RMSE': prophet_metrics['RMSE'],
                'Manual_MAPE': manual_metrics['MAPE'],
                'Manual_WMAPE': manual_metrics['WMAPE'],
                'Manual_Bias': manual_metrics['Bias'],
                'Manual_RMSE': manual_metrics['RMSE'],
                'Better_Method': 'Prophet' if prophet_metrics['WMAPE'] < manual_metrics['WMAPE'] else 'Manual',
                'WMAPE_Improvement': manual_metrics['WMAPE'] - prophet_metrics['WMAPE']
            }
            
            comparison_results.append(result)
    
    if comparison_results:
        return pd.DataFrame(comparison_results)
    else:
        return pd.DataFrame()


def generate_comparison_summary(comparison_df: pd.DataFrame) -> Dict:
    """
    Generate summary statistics for the comparison.
    
    Args:
        comparison_df: DataFrame with comparison metrics
        
    Returns:
        Dictionary with summary statistics
    """
    if len(comparison_df) == 0:
        return {}
    
    # Check if required columns exist
    required_columns = ['Better_Method', 'Prophet_WMAPE', 'Manual_WMAPE', 'WMAPE_Improvement']
    if not all(col in comparison_df.columns for col in required_columns):
        return {}
    
    try:
        summary = {
            'Total_Products': len(comparison_df),
            'Prophet_Better_Count': len(comparison_df[comparison_df['Better_Method'] == 'Prophet']) if 'Better_Method' in comparison_df.columns else 0,
            'Manual_Better_Count': len(comparison_df[comparison_df['Better_Method'] == 'Manual']) if 'Better_Method' in comparison_df.columns else 0,
            'Avg_Prophet_WMAPE': comparison_df['Prophet_WMAPE'].mean() if 'Prophet_WMAPE' in comparison_df.columns else 0,
            'Avg_Manual_WMAPE': comparison_df['Manual_WMAPE'].mean() if 'Manual_WMAPE' in comparison_df.columns else 0,
            'Avg_WMAPE_Improvement': comparison_df['WMAPE_Improvement'].mean() if 'WMAPE_Improvement' in comparison_df.columns else 0,
            'Median_Prophet_WMAPE': comparison_df['Prophet_WMAPE'].median() if 'Prophet_WMAPE' in comparison_df.columns else 0,
            'Median_Manual_WMAPE': comparison_df['Manual_WMAPE'].median() if 'Manual_WMAPE' in comparison_df.columns else 0,
        }
        
        return summary
    except Exception:
        return {}


def prepare_forecast_output(prophet_forecasts: pd.DataFrame,
                           comparison_df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare a comprehensive output DataFrame with forecasts and comparison.
    
    Args:
        prophet_forecasts: DataFrame with Prophet forecasts
        comparison_df: DataFrame with comparison metrics
        
    Returns:
        Combined DataFrame with forecasts and metrics
    """
    # Start with prophet forecasts
    output = prophet_forecasts.copy()
    
    # Only merge if comparison_df has data and required columns
    if len(comparison_df) > 0:
        required_columns = ['Sales Force', 'Product PA', 'Prophet_WMAPE', 'Manual_WMAPE', 'Better_Method']
        if all(col in comparison_df.columns for col in required_columns):
            # Merge forecasts with comparison metrics
            output = output.merge(
                comparison_df[required_columns],
                on=['Sales Force', 'Product PA'],
                how='left'
            )
        else:
            # If columns are missing, just add empty columns
            for col in ['Prophet_WMAPE', 'Manual_WMAPE', 'Better_Method']:
                if col not in output.columns:
                    output[col] = np.nan
    else:
        # If comparison_df is empty, add empty columns
        for col in ['Prophet_WMAPE', 'Manual_WMAPE', 'Better_Method']:
            if col not in output.columns:
                output[col] = np.nan
    
    # Sort by date and product
    output = output.sort_values(['Sales Force', 'Product PA', 'Date']).reset_index(drop=True)
    
    return output

