# Sales Forecasting with Prophet

A Python application for generating sales forecasts using Meta's Prophet model, with comparison capabilities against manual forecasts from sales teams.

## Features

- **Automated Forecasting**: Uses Prophet model to generate monthly sales forecasts
- **Manual Forecast Comparison**: Compares Prophet forecasts with manual forecasts from sales teams
- **Accuracy Metrics**: Calculates WMAPE, MAPE, Bias, and RMSE for both methods
- **User-Friendly Interface**: Simple Streamlit web interface - no programming knowledge required
- **Visualizations**: Interactive charts showing actuals, forecasts, and confidence intervals
- **Excel Export**: Download forecasts and comparison results as Excel files

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone or download this repository

2. Install required packages:
```bash
pip install -r requirements.txt
```

Note: Prophet requires additional system dependencies. If you encounter installation issues:

**Windows:**
```bash
# Prophet installation may require Visual C++ Build Tools
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
```

**Linux/Mac:**
```bash
# Usually works with standard pip install
pip install prophet
```

## Usage

### Running the Application

1. Start the Streamlit application:
```bash
streamlit run app.py
```

2. The application will open in your web browser automatically (usually at `http://localhost:8501`)

3. Upload your Excel file using the sidebar

4. Click "Generate Forecasts" to create predictions

5. Explore the results in the different tabs:
   - **Forecasts**: View Prophet and manual forecasts
   - **Comparison**: See accuracy metrics comparison
   - **Visualizations**: Interactive charts for each product
   - **Download**: Export results as Excel file

### Data Format

Your Excel file should follow this structure:

- **Columns**: 
  - `Sales Force`: Sales force identifier
  - `Product PA`: Product identifier (can repeat for different Sales Forces)
  - `Key Figure`: Must include:
    - `Actuals Qty`: Real sales data
    - `Consensus Demand Final`: Manual forecasts from sales team
  - **Monthly columns**: Date columns in format "YY-MMM" (e.g., "21-Jan", "22-Feb", "25-Aug")

### Example Data Structure

| Sales Force | Product PA | Key Figure | 21-Jan | 21-Feb | ... | 25-Aug |
|------------|------------|------------|--------|--------|-----|--------|
| HPC | PA07C0 | Actuals Qty | 1500 | 1600 | ... | 1489 |
| HPC | PA07C0 | Consensus Demand Final | 1550 | 1586 | ... | 1500 |

## Project Structure

```
.
├── app.py                      # Main Streamlit application
├── data_processor.py           # Data loading and transformation
├── prophet_forecaster.py       # Prophet model implementation
├── forecast_comparison.py      # Comparison and accuracy metrics
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## How It Works

1. **Data Processing**: 
   - Reads Excel file in wide format (months as columns)
   - Transforms to long format for analysis
   - Extracts actuals and manual forecasts

2. **Forecasting**:
   - Trains Prophet model for each unique Sales Force + Product PA combination
   - Generates forecasts for specified number of future months
   - Includes confidence intervals

3. **Comparison**:
   - Compares Prophet forecasts with manual forecasts
   - Calculates accuracy metrics (WMAPE, MAPE, Bias, RMSE)
   - Identifies which method performs better for each product

4. **Output**:
   - Displays forecasts in interactive tables
   - Creates visualizations showing trends and predictions
   - Exports results to Excel for further analysis

## Accuracy Metrics

- **WMAPE** (Weighted Mean Absolute Percentage Error): Percentage error weighted by actual values
- **MAPE** (Mean Absolute Percentage Error): Average percentage error
- **Bias**: Mean error (positive = over-forecast, negative = under-forecast)
- **RMSE** (Root Mean Squared Error): Standard deviation of prediction errors

## Troubleshooting

### Prophet Installation Issues

If you encounter errors installing Prophet:

1. **Windows**: Install Microsoft Visual C++ Build Tools
2. **Linux**: Install build-essential: `sudo apt-get install build-essential`
3. **Mac**: Install Xcode Command Line Tools: `xcode-select --install`

### Data Loading Errors

- Ensure your Excel file follows the expected format
- Check that "Actuals Qty" and "Consensus Demand Final" exist in the Key Figure column
- Verify date columns are in "YY-MMM" format

### Forecast Generation Errors

- Ensure you have at least 3 months of historical data for each product
- Check for missing or invalid date values
- Verify that actuals values are positive numbers

## Monthly Updates

To update forecasts with new monthly data:

1. Add the new month's data to your Excel file (new column with format "YY-MMM")
2. Upload the updated file to the application
3. Click "Generate Forecasts" to create updated predictions
4. Download the new results

## Support

For issues or questions, please check:
- Prophet documentation: https://facebook.github.io/prophet/
- Streamlit documentation: https://docs.streamlit.io/

## License

This project is provided as-is for sales forecasting purposes.

