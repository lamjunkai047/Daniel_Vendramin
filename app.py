"""
Streamlit application for sales forecasting using Prophet.
Simple interface for non-programmers to upload data and generate forecasts.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import warnings
warnings.filterwarnings('ignore')

from data_processor import (
    read_excel_file,
    transform_to_long_format,
    extract_actuals_and_forecasts,
    get_unique_combinations
)
from prophet_forecaster import forecast_by_product
from forecast_comparison import compare_forecasts, generate_comparison_summary, prepare_forecast_output

# Page configuration
st.set_page_config(
    page_title="Sales Forecasting with Prophet",
    page_icon="📈",
    layout="wide"
)

# Title
st.title("📈 Sales Forecasting with Prophet")
st.markdown("Upload your sales data file to generate forecasts and compare with manual predictions.")

# Sidebar for file upload and settings
with st.sidebar:
    st.header("📁 Upload Data")
    uploaded_file = st.file_uploader(
        "Choose an Excel file",
        type=['xlsx', 'xls'],
        help="Upload your monthly sales data file (Max 200MB). For large files, please wait for upload to complete.",
        accept_multiple_files=False
    )
    
    # Show file info if uploaded
    if uploaded_file is not None:
        file_size_mb = uploaded_file.size / (1024 * 1024)
        st.info(f"📄 File: {uploaded_file.name}\n📊 Size: {file_size_mb:.2f} MB")
        
        if file_size_mb > 200:
            st.error("⚠️ File is too large! Maximum size is 200MB. Please use a smaller file.")
            uploaded_file = None
        elif file_size_mb > 50:
            st.warning("⚠️ Large file detected. Upload and processing may take longer. Please be patient.")
    
    st.header("⚙️ Forecast Settings")
    forecast_periods = st.number_input(
        "Number of months to forecast",
        min_value=1,
        max_value=24,
        value=12,
        help="How many months into the future to predict"
    )
    
    st.header("ℹ️ About")
    st.info("""
    This application uses Meta's Prophet model to generate sales forecasts.
    
    **Features:**
    - Automatic forecast generation
    - Comparison with manual forecasts
    - Accuracy metrics (WMAPE, MAPE, Bias)
    - Visualizations
    """)

# Main content area
if uploaded_file is not None:
    try:
        # Check file size again
        file_size_mb = uploaded_file.size / (1024 * 1024)
        if file_size_mb > 200:
            st.error("❌ File is too large! Maximum size is 200MB.")
            st.stop()
        
        # Show progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Read and process data with progress updates
        status_text.text("📥 Reading Excel file...")
        progress_bar.progress(10)
        
        # Reset file pointer in case it was read before
        uploaded_file.seek(0)
        
        # Read file with error handling
        try:
            df_raw = read_excel_file(uploaded_file)
        except Exception as read_error:
            progress_bar.empty()
            status_text.empty()
            if "canceled" in str(read_error).lower():
                st.error("❌ File upload was canceled. Please try uploading again.")
            else:
                st.error(f"❌ Error reading file: {str(read_error)}")
                st.info("💡 Please ensure the file is a valid Excel file (.xlsx or .xls)")
            st.stop()
        
        status_text.text("🔄 Transforming data format...")
        progress_bar.progress(30)
        df_long = transform_to_long_format(df_raw)
        
        status_text.text("📊 Extracting actuals and forecasts...")
        progress_bar.progress(60)
        actuals_df, forecasts_df = extract_actuals_and_forecasts(df_long)
        
        status_text.text("💾 Storing data...")
        progress_bar.progress(80)
        
        # Store in session state
        st.session_state['actuals_df'] = actuals_df
        st.session_state['forecasts_df'] = forecasts_df
        st.session_state['df_raw'] = df_raw
        
        progress_bar.progress(100)
        status_text.text("✅ Complete!")
        
        # Clear progress indicators
        import time
        time.sleep(0.5)
        progress_bar.empty()
        status_text.empty()
        
        st.success("✅ Data loaded successfully!")
        
        # Display data summary
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Products", len(get_unique_combinations(actuals_df)))
        with col2:
            st.metric("Date Range", f"{actuals_df['Date'].min().strftime('%Y-%m')} to {actuals_df['Date'].max().strftime('%Y-%m')}")
        with col3:
            st.metric("Total Records", len(actuals_df))
        with col4:
            st.metric("Sales Forces", actuals_df['Sales Force'].nunique())
        
        # Generate forecasts button
        if st.button("🚀 Generate Forecasts", type="primary", use_container_width=True):
            with st.spinner("Generating forecasts with Prophet... This may take a few minutes."):
                try:
                    # Generate Prophet forecasts
                    prophet_forecasts = forecast_by_product(
                        actuals_df,
                        forecasts_df,
                        periods=forecast_periods
                    )
                    
                    if len(prophet_forecasts) > 0:
                        # Initialize manual forecasts input dataframe
                        manual_input_df = prophet_forecasts[['Sales Force', 'Product PA', 'Date']].copy()
                        # Merge with existing manual forecasts if available
                        if len(forecasts_df) > 0:
                            forecasts_df_copy = forecasts_df.copy()
                            forecasts_df_copy['Date'] = pd.to_datetime(forecasts_df_copy['Date']).dt.to_period('M').dt.to_timestamp()
                            manual_input_df['Date'] = pd.to_datetime(manual_input_df['Date']).dt.to_period('M').dt.to_timestamp()
                            manual_input_df = manual_input_df.merge(
                                forecasts_df_copy[['Sales Force', 'Product PA', 'Date', 'Manual_Forecast']],
                                on=['Sales Force', 'Product PA', 'Date'],
                                how='left'
                            )
                        else:
                            manual_input_df['Manual_Forecast'] = None
                        st.session_state['manual_forecasts_input'] = manual_input_df
                        
                        # Compare forecasts
                        comparison_df = compare_forecasts(
                            prophet_forecasts,
                            actuals_df,
                            forecasts_df
                        )
                        
                        # Generate summary
                        summary = generate_comparison_summary(comparison_df)
                        
                        # Store in session state
                        st.session_state['prophet_forecasts'] = prophet_forecasts
                        st.session_state['comparison_df'] = comparison_df
                        st.session_state['summary'] = summary
                        st.session_state['forecasts_df'] = forecasts_df  # Store for later use
                        
                        st.success("✅ Forecasts generated successfully!")
                    else:
                        st.error("❌ No forecasts could be generated. Please check your data.")
                        
                except Exception as e:
                    st.error(f"❌ Error generating forecasts: {str(e)}")
                    st.exception(e)
        
        # Display results if available
        if 'prophet_forecasts' in st.session_state and len(st.session_state['prophet_forecasts']) > 0:
            st.divider()
            st.header("📊 Forecast Results")
            
            # Summary metrics
            if 'summary' in st.session_state and st.session_state['summary']:
                summary = st.session_state['summary']
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric(
                        "Prophet Better",
                        f"{summary.get('Prophet_Better_Count', 0)}/{summary.get('Total_Products', 0)}",
                        help="Number of products where Prophet outperforms manual forecasts"
                    )
                with col2:
                    st.metric(
                        "Avg Prophet WMAPE",
                        f"{summary.get('Avg_Prophet_WMAPE', 0):.2f}%",
                        delta=f"{summary.get('Avg_WMAPE_Improvement', 0):.2f}%",
                        delta_color="inverse",
                        help="Average Weighted Mean Absolute Percentage Error"
                    )
                with col3:
                    st.metric(
                        "Avg Manual WMAPE",
                        f"{summary.get('Avg_Manual_WMAPE', 0):.2f}%",
                        help="Average WMAPE for manual forecasts"
                    )
                with col4:
                    improvement = summary.get('Avg_WMAPE_Improvement', 0)
                    st.metric(
                        "WMAPE Improvement",
                        f"{improvement:.2f}%",
                        delta="Better" if improvement > 0 else "Worse",
                        help="Improvement of Prophet over Manual (positive is better)"
                    )
            
            # Tabs for different views
            tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Forecasts", "✏️ Edit Manual Forecasts", "📊 Comparison", "📉 Visualizations", "💾 Download"])
            
            with tab1:
                st.subheader("Prophet Forecasts")
                # Get available columns
                available_cols = st.session_state['prophet_forecasts'].columns.tolist()
                display_cols = ['Sales Force', 'Product PA', 'Date', 'Prophet_Forecast', 
                               'Prophet_Lower', 'Prophet_Upper', 'Manual_Forecast']
                # Only include columns that exist
                display_cols = [col for col in display_cols if col in available_cols]
                
                forecast_display = st.session_state['prophet_forecasts'][display_cols].copy()
                if 'Date' in forecast_display.columns:
                    forecast_display['Date'] = forecast_display['Date'].dt.strftime('%Y-%m')
                forecast_display = forecast_display.round(2)
                st.dataframe(forecast_display, use_container_width=True)
            
            with tab2:
                st.subheader("✏️ Edit Manual Forecasts")
                st.markdown("Enter or edit manual forecasts for comparison with Prophet predictions.")
                
                # Filter options
                col_filter1, col_filter2 = st.columns(2)
                with col_filter1:
                    sales_force_filter = st.selectbox(
                        "Filter by Sales Force",
                        options=['All'] + sorted(st.session_state['prophet_forecasts']['Sales Force'].unique().tolist()),
                        key='manual_sf_filter'
                    )
                with col_filter2:
                    product_filter = st.selectbox(
                        "Filter by Product",
                        options=['All'] + sorted(st.session_state['prophet_forecasts']['Product PA'].unique().tolist()),
                        key='manual_prod_filter'
                    )
                
                # Initialize manual forecasts in session state if not exists
                if 'manual_forecasts_input' not in st.session_state:
                    # Create a DataFrame with all forecast combinations
                    prophet_forecasts = st.session_state['prophet_forecasts'].copy()
                    manual_input_df = prophet_forecasts[['Sales Force', 'Product PA', 'Date']].copy()
                    # Get existing manual forecasts from the forecasts_df if available
                    if 'forecasts_df' in st.session_state:
                        existing_manual = st.session_state['forecasts_df'].copy()
                        existing_manual['Date'] = pd.to_datetime(existing_manual['Date']).dt.to_period('M').dt.to_timestamp()
                        manual_input_df['Date'] = pd.to_datetime(manual_input_df['Date']).dt.to_period('M').dt.to_timestamp()
                        manual_input_df = manual_input_df.merge(
                            existing_manual[['Sales Force', 'Product PA', 'Date', 'Manual_Forecast']],
                            on=['Sales Force', 'Product PA', 'Date'],
                            how='left'
                        )
                    else:
                        manual_input_df['Manual_Forecast'] = None
                    st.session_state['manual_forecasts_input'] = manual_input_df
                
                # Display editable dataframe
                st.markdown("**Edit the values in the table below and click 'Update Manual Forecasts' to save:**")
                
                # Prepare data for editing
                edit_df = st.session_state['manual_forecasts_input'].copy()
                # Ensure Date is datetime
                if not pd.api.types.is_datetime64_any_dtype(edit_df['Date']):
                    edit_df['Date'] = pd.to_datetime(edit_df['Date'])
                
                # Apply filters
                if sales_force_filter != 'All':
                    edit_df = edit_df[edit_df['Sales Force'] == sales_force_filter]
                if product_filter != 'All':
                    edit_df = edit_df[edit_df['Product PA'] == product_filter]
                
                # Format date for display
                edit_df_display = edit_df.copy()
                edit_df_display['Date'] = edit_df_display['Date'].dt.strftime('%Y-%m')
                
                # Use data_editor for editing
                edited_df = st.data_editor(
                    edit_df_display,
                    column_config={
                        "Sales Force": st.column_config.TextColumn("Sales Force", disabled=True),
                        "Product PA": st.column_config.TextColumn("Product PA", disabled=True),
                        "Date": st.column_config.TextColumn("Date", disabled=True),
                        "Manual_Forecast": st.column_config.NumberColumn(
                            "Manual Forecast",
                            min_value=0.0,
                            format="%.2f",
                            help="Enter manual forecast value"
                        )
                    },
                    hide_index=True,
                    use_container_width=True,
                    num_rows="fixed"
                )
                
                # Update button
                col1, col2 = st.columns([1, 4])
                with col1:
                    if st.button("💾 Update Manual Forecasts", type="primary"):
                        # Convert back to datetime for matching
                        edited_df['Date'] = pd.to_datetime(edited_df['Date'])
                        
                        # Update the full manual_forecasts_input with edited values
                        full_df = st.session_state['manual_forecasts_input'].copy()
                        full_df['Date'] = pd.to_datetime(full_df['Date']).dt.to_period('M').dt.to_timestamp()
                        edited_df['Date'] = pd.to_datetime(edited_df['Date']).dt.to_period('M').dt.to_timestamp()
                        
                        # Merge to update values
                        full_df = full_df.drop(columns=['Manual_Forecast'], errors='ignore')
                        full_df = full_df.merge(
                            edited_df[['Sales Force', 'Product PA', 'Date', 'Manual_Forecast']],
                            on=['Sales Force', 'Product PA', 'Date'],
                            how='left'
                        )
                        
                        # Update session state
                        st.session_state['manual_forecasts_input'] = full_df
                        
                        # Update the forecasts_df in session state
                        updated_forecasts = edited_df[['Sales Force', 'Product PA', 'Date', 'Manual_Forecast']].copy()
                        updated_forecasts = updated_forecasts[updated_forecasts['Manual_Forecast'].notna()]
                        updated_forecasts.columns = ['Sales Force', 'Product PA', 'Date', 'Manual_Forecast']
                        st.session_state['forecasts_df'] = updated_forecasts
                        
                        # Re-merge with Prophet forecasts
                        prophet_forecasts = st.session_state['prophet_forecasts'].copy()
                        prophet_forecasts['Date'] = pd.to_datetime(prophet_forecasts['Date']).dt.to_period('M').dt.to_timestamp()
                        updated_forecasts['Date'] = pd.to_datetime(updated_forecasts['Date']).dt.to_period('M').dt.to_timestamp()
                        
                        prophet_forecasts = prophet_forecasts.drop(columns=['Manual_Forecast'], errors='ignore')
                        prophet_forecasts = prophet_forecasts.merge(
                            updated_forecasts[['Sales Force', 'Product PA', 'Date', 'Manual_Forecast']],
                            on=['Sales Force', 'Product PA', 'Date'],
                            how='left'
                        )
                        st.session_state['prophet_forecasts'] = prophet_forecasts
                        
                        # Recalculate comparison if we have actuals
                        if 'actuals_df' in st.session_state:
                            try:
                                comparison_df = compare_forecasts(
                                    prophet_forecasts,
                                    st.session_state['actuals_df'],
                                    updated_forecasts
                                )
                                summary = generate_comparison_summary(comparison_df)
                                st.session_state['comparison_df'] = comparison_df
                                st.session_state['summary'] = summary
                            except:
                                pass
                        
                        st.success("✅ Manual forecasts updated! Comparison metrics have been recalculated.")
                        st.rerun()
                
                st.markdown("---")
                st.info("💡 **Tip:** You can edit multiple values at once. After making changes, click 'Update Manual Forecasts' to save and recalculate comparisons.")
            
            with tab3:
                st.subheader("Forecast Comparison")
                if 'comparison_df' in st.session_state and len(st.session_state['comparison_df']) > 0:
                    comparison_display = st.session_state['comparison_df'].copy()
                    comparison_display = comparison_display.round(2)
                    st.dataframe(comparison_display, use_container_width=True)
                else:
                    st.info("Comparison metrics will be calculated when historical data is available.")
            
            with tab4:
                st.subheader("Forecast Visualizations")
                
                # Product selector
                combinations = get_unique_combinations(actuals_df)
                selected_product = st.selectbox(
                    "Select Product to Visualize",
                    options=range(len(combinations)),
                    format_func=lambda x: f"{combinations.iloc[x]['Sales Force']} - {combinations.iloc[x]['Product PA']}"
                )
                
                if selected_product is not None:
                    selected_row = combinations.iloc[selected_product]
                    sales_force = selected_row['Sales Force']
                    product_pa = selected_row['Product PA']
                    
                    # Get data for selected product
                    product_actuals = actuals_df[
                        (actuals_df['Sales Force'] == sales_force) & 
                        (actuals_df['Product PA'] == product_pa)
                    ].copy()
                    
                    product_prophet = st.session_state['prophet_forecasts'][
                        (st.session_state['prophet_forecasts']['Sales Force'] == sales_force) & 
                        (st.session_state['prophet_forecasts']['Product PA'] == product_pa)
                    ].copy()
                    
                    # Get manual forecasts from session state (updated ones)
                    if 'forecasts_df' in st.session_state:
                        product_manual = st.session_state['forecasts_df'][
                            (st.session_state['forecasts_df']['Sales Force'] == sales_force) & 
                            (st.session_state['forecasts_df']['Product PA'] == product_pa)
                        ].copy()
                    else:
                        product_manual = pd.DataFrame()
                    
                    # Create visualization
                    fig = go.Figure()
                    
                    # Historical actuals
                    fig.add_trace(go.Scatter(
                        x=product_actuals['Date'],
                        y=product_actuals['Actuals'],
                        mode='lines+markers',
                        name='Actuals',
                        line=dict(color='blue', width=2)
                    ))
                    
                    # Prophet forecast
                    fig.add_trace(go.Scatter(
                        x=product_prophet['Date'],
                        y=product_prophet['Prophet_Forecast'],
                        mode='lines+markers',
                        name='Prophet Forecast',
                        line=dict(color='green', width=2, dash='dash')
                    ))
                    
                    # Prophet confidence interval
                    fig.add_trace(go.Scatter(
                        x=product_prophet['Date'],
                        y=product_prophet['Prophet_Upper'],
                        mode='lines',
                        name='Prophet Upper',
                        line=dict(width=0),
                        showlegend=False
                    ))
                    fig.add_trace(go.Scatter(
                        x=product_prophet['Date'],
                        y=product_prophet['Prophet_Lower'],
                        mode='lines',
                        name='Prophet Confidence',
                        fill='tonexty',
                        fillcolor='rgba(0,255,0,0.2)',
                        line=dict(width=0)
                    ))
                    
                    # Manual forecast
                    if len(product_manual) > 0:
                        fig.add_trace(go.Scatter(
                            x=product_manual['Date'],
                            y=product_manual['Manual_Forecast'],
                            mode='lines+markers',
                            name='Manual Forecast',
                            line=dict(color='red', width=2, dash='dot')
                        ))
                    
                    fig.update_layout(
                        title=f"Sales Forecast: {sales_force} - {product_pa}",
                        xaxis_title="Date",
                        yaxis_title="Quantity",
                        hovermode='x unified',
                        height=500
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
            
            with tab5:
                st.subheader("Download Results")
                
                output = BytesIO()
                try:
                    # Prepare download data
                    comparison_df = st.session_state.get('comparison_df', pd.DataFrame())
                    output_df = prepare_forecast_output(
                        st.session_state['prophet_forecasts'],
                        comparison_df
                    )
                    
                    # Convert to Excel
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        output_df.to_excel(writer, sheet_name='Forecasts', index=False)
                        if len(comparison_df) > 0 and 'Prophet_WMAPE' in comparison_df.columns:
                            comparison_df.to_excel(
                                writer, sheet_name='Comparison', index=False
                            )
                except Exception as e:
                    st.warning(f"Note: Some comparison data may not be available. Exporting forecasts only.")
                    # Fallback: just export forecasts
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        st.session_state['prophet_forecasts'].to_excel(
                            writer, sheet_name='Forecasts', index=False
                        )
                
                output.seek(0)
                
                st.download_button(
                    label="📥 Download Forecasts (Excel)",
                    data=output,
                    file_name="prophet_forecasts.xlsx",
                    mime="application/vnd.openpyxl-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
        
    except pd.errors.EmptyDataError:
        st.error("❌ The uploaded file is empty. Please upload a valid Excel file with data.")
    except pd.errors.ParserError as e:
        st.error(f"❌ Error reading Excel file: {str(e)}")
        st.info("💡 Please ensure your file is a valid Excel file (.xlsx or .xls format)")
    except Exception as e:
        error_msg = str(e)
        if "canceled" in error_msg.lower() or "CanceledError" in str(type(e)):
            st.error("❌ File upload was canceled or timed out.")
            st.info("""
            **Possible causes:**
            - File is too large (try a smaller file or compress it)
            - Slow internet connection
            - Upload timeout
            
            **Solutions:**
            - Try uploading a smaller file (< 50MB recommended)
            - Check your internet connection
            - Try again in a few moments
            """)
        elif "memory" in error_msg.lower():
            st.error("❌ Not enough memory to process this file.")
            st.info("💡 Please try with a smaller file or reduce the number of rows.")
        else:
            st.error(f"❌ Error processing file: {error_msg}")
            with st.expander("🔍 Technical Details"):
                st.exception(e)

else:
    # Instructions when no file is uploaded
    st.info("👆 Please upload your sales data file using the sidebar to get started.")
    
    st.markdown("""
    ### How to use:
    1. **Upload Data**: Click "Browse files" in the sidebar and select your Excel file
    2. **Review Summary**: Check the data summary to ensure your file loaded correctly
    3. **Generate Forecasts**: Click the "Generate Forecasts" button
    4. **View Results**: Explore forecasts, comparisons, and visualizations in the tabs
    5. **Download**: Export your results as an Excel file
    
    ### Data Format:
    Your Excel file should contain:
    - **Sales Force**: Sales force identifier
    - **Product PA**: Product identifier
    - **Key Figure**: Should include "Actuals Qty" and "Consensus Demand Final"
    - **Monthly columns**: Date columns in format "YY-MMM" (e.g., "21-Jan", "22-Feb")
    """)

