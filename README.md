# Portfolio Trade Analysis Tool

## Overview

The **Portfolio Trade Analysis Tool** is a Python-based script designed to analyze trading portfolios, calculate key financial metrics, and rank accounts based on their performance. This tool helps investors and analysts assess portfolio performance and identify the top-performing accounts using data-driven insights.

## Features

- **Data Validation and Cleaning**: Ensures data integrity by handling invalid or corrupted JSON entries in the trade history.
- **Financial Metric Calculation**:
  - Profit and Loss (PnL)
  - Return on Investment (ROI)
  - Win Rate
  - Sharpe Ratio
  - Maximum Drawdown (MDD)
- **Account Ranking**: Uses a weighted scoring system to rank accounts and extract the top 20 performers.
- **CSV Export**: Outputs results into a user-friendly CSV format for further analysis.

## Requirements

The script relies on the following Python libraries:

- `pandas`: Data manipulation and cleaning.
- `numpy`: Numerical operations.
- `json`: JSON parsing.
- `ast`: Safe evaluation of Python literals.
- `typing`: Type hints for improved code readability.

To install the required libraries, run:

```bash
pip install pandas numpy
```

## Usage

1. **Prepare Input Data**: 
   - Ensure your dataset is in CSV format and contains the following columns:
     - `Port_IDs`: Unique account identifiers.
     - `Trade_History`: Trade history in JSON format.
   - Save the file as `trade_data.csv` or specify a different name when running the script.

2. **Run the Script**:
   - Execute the script from the command line:
     ```bash
     python trade_analysis.py
     ```
   - By default, the input file is `trade_data.csv`, and the output file is `top_20_accounts.csv`.

3. **View Output**:
   - The script generates a CSV file with the top 20 ranked accounts, including metrics like PnL, ROI, Win Rate, and more.

## File Structure

- **Input File (`trade_data.csv`)**: Contains trade data.
- **Output File (`top_20_accounts.csv`)**: Contains the top 20 ranked accounts with their metrics.

## Key Functions

#### `validate_json_string(json_str: str) -> Union[Dict, List, None]`
Parses and validates JSON strings in the dataset.

#### `load_and_clean_data(file_path: str) -> pd.DataFrame`
Loads and cleans the input dataset, removing invalid rows and normalizing trade history data.

#### `calculate_metrics(trade_df: pd.DataFrame) -> pd.DataFrame`
Calculates key financial metrics for each account.

#### `rank_accounts(metrics_df: pd.DataFrame) -> pd.DataFrame`
Ranks accounts based on a weighted scoring system and extracts the top 20.

#### `save_metrics(metrics_df: pd.DataFrame, output_path: str)`
Saves the calculated metrics and rankings to a CSV file.

## Error Handling

- Handles missing or invalid JSON data in the trade history.
- Validates the presence of required columns (`Port_IDs`, `Trade_History`).
- Warns of accounts with incomplete data or missing metrics.
- Ensures that all calculations account for edge cases, such as division by zero.

## Customization

- **Input and Output File Paths**: Modify the `input_file` and `output_file` variables in the script to change the file locations.
- **Ranking Weights**: Adjust the weights in the `rank_accounts` function to prioritize specific metrics.

## Example

Input (CSV): [Source](https://drive.google.com/drive/folders/1ioZ56B5-zTmFuPrT7IihjOVozAgrXxhl?usp=sharing)

| Port_IDs | Trade_History                                                                                  |
|----------|-----------------------------------------------------------------------------------------------|
| 1        | [{"price": 100, "quantity": 2, "realizedProfit": 10}, {"price": 105, "quantity": 2, "realizedProfit": 15}] |
| 2        | [{"price": 200, "quantity": 1, "realizedProfit": -5}, {"price": 210, "quantity": 1, "realizedProfit": 5}] |

Output (CSV):

| Port_IDs | PnL  | ROI    | Win_Rate | Win_Positions | Total_Positions | Sharpe_Ratio | MDD | Rank |
|----------|------|--------|----------|---------------|-----------------|--------------|-----|------|
| 1        | 25.0 | 0.05   | 1.0      | 2             | 2               | 1.5          | 0.0 | 1    |
| 2        | 0.0  | -0.025 | 0.5      | 1             | 2               | 0.0          | 5.0 | 2    |
