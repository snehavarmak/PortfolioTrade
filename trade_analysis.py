import pandas as pd
import numpy as np
import json
import ast
from typing import Union, Dict, List

def validate_json_string(json_str: str) -> Union[Dict, List, None]:
    if pd.isna(json_str):
        return None
        
    try:
        # First try direct JSON parsing
        return json.loads(json_str)
    except json.JSONDecodeError:
        try:
            # Try evaluating as Python literal (for cases with single quotes)
            data = ast.literal_eval(json_str)
            # Convert to proper JSON format
            return json.loads(json.dumps(data))
        except (ValueError, SyntaxError, json.JSONDecodeError):
            return None

def load_and_clean_data(file_path: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"Could not find the file at: {file_path}")
    except Exception as e:
        raise ValueError(f"Error reading CSV file: {str(e)}")
    
    # Check for required columns
    required_columns = ['Port_IDs', 'Trade_History']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Dataset is missing required columns: {missing_columns}")
    
    # Parse the 'Trade_History' column with validation
    print("Parsing Trade_History column...")
    df['Trade_History'] = df['Trade_History'].apply(validate_json_string)
    
    # Remove rows with invalid JSON
    invalid_rows = df['Trade_History'].isna()
    if invalid_rows.any():
        print(f"Warning: Removed {invalid_rows.sum()} rows with invalid JSON data")
        df = df[~invalid_rows]
    
    if df.empty:
        raise ValueError("No valid trade data remaining after cleaning")
    
    # Normalize the Trade_History into columns
    try:
        trade_data = df.explode('Trade_History')
        json_normalized = pd.json_normalize(trade_data['Trade_History'].dropna())
        
        # Merge normalized data with original dataframe
        trade_data = pd.concat([
            trade_data.drop(['Trade_History'], axis=1).reset_index(drop=True),
            json_normalized.reset_index(drop=True)
        ], axis=1)
        
    except Exception as e:
        raise ValueError(f"Error normalizing trade data: {str(e)}")
    
    # Handle missing values and duplicates
    trade_data = trade_data.drop_duplicates()
    
    # Replace infinite values with NaN and then drop
    trade_data = trade_data.replace([np.inf, -np.inf], np.nan)
    trade_data = trade_data.dropna()
    
    return trade_data

def calculate_metrics(trade_df: pd.DataFrame) -> pd.DataFrame:
    if trade_df.empty:
        raise ValueError("Empty DataFrame provided for metrics calculation")
        
    accounts = trade_df['Port_IDs'].unique()
    metrics = []
    
    required_columns = ['price', 'quantity', 'realizedProfit']
    missing_columns = [col for col in required_columns if col not in trade_df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns for metrics calculation: {missing_columns}")

    for account in accounts:
        try:
            account_data = trade_df[trade_df['Port_IDs'] == account]
            
            # Calculate PnL with safe operations
            pnl = account_data['realizedProfit'].sum()
            
            # Calculate ROI with safety checks
            initial_balance = 0
            final_balance = 0
            
            if not account_data.empty:
                initial_balance = account_data.iloc[0]['price'] * account_data.iloc[0]['quantity']
                final_balance = account_data.iloc[-1]['price'] * account_data.iloc[-1]['quantity']
            
            roi = ((final_balance - initial_balance) / initial_balance) if initial_balance != 0 else 0
            
            # Calculate Win Rate
            win_positions = len(account_data[account_data['realizedProfit'] > 0])
            total_positions = len(account_data)
            win_rate = win_positions / total_positions if total_positions > 0 else 0
            
            # Calculate Sharpe Ratio with error handling
            returns = account_data['realizedProfit']
            mean_return = returns.mean() if not returns.empty else 0
            std_return = returns.std() if not returns.empty else 1
            sharpe_ratio = mean_return / std_return if std_return != 0 else 0
            
            # Calculate Maximum Drawdown (MDD)
            cumulative_profit = returns.cumsum()
            max_profit = cumulative_profit.cummax()
            drawdown = max_profit - cumulative_profit
            max_drawdown = drawdown.max() if not drawdown.empty else 0
            
            metrics.append({
                'Port_IDs': account,
                'PnL': pnl,
                'ROI': roi,
                'Win_Rate': win_rate,
                'Win_Positions': win_positions,
                'Total_Positions': total_positions,
                'Sharpe_Ratio': sharpe_ratio,
                'MDD': max_drawdown
            })
            
        except Exception as e:
            print(f"Warning: Error calculating metrics for account {account}: {str(e)}")
            continue
    
    if not metrics:
        raise ValueError("No valid metrics could be calculated")
    
    return pd.DataFrame(metrics)

# Ranking Algorithm
def rank_accounts(metrics_df):
  
    # Define weighted scoring system
    weights = {
        'ROI': 0.4,
        'PnL': 0.3,
        'Sharpe_Ratio': 0.2,
        'Win_Rate': 0.1
    }
    
    # Normalize metrics and calculate scores
    for col in ['ROI', 'PnL', 'Sharpe_Ratio', 'Win_Rate']:
        metrics_df[f'{col}_normalized'] = (metrics_df[col] - metrics_df[col].min()) / (metrics_df[col].max() - metrics_df[col].min())
    
    metrics_df['Score'] = (
        weights['ROI'] * metrics_df['ROI_normalized'] +
        weights['PnL'] * metrics_df['PnL_normalized'] +
        weights['Sharpe_Ratio'] * metrics_df['Sharpe_Ratio_normalized'] +
        weights['Win_Rate'] * metrics_df['Win_Rate_normalized']
    )
    
    # Rank accounts
    metrics_df['Rank'] = metrics_df['Score'].rank(ascending=False)
    top_20_accounts = metrics_df.nsmallest(20, 'Rank')
    
    return top_20_accounts

# Generate CSV Output
def save_metrics(metrics_df, output_path):
  
    metrics_df.to_csv(output_path, index=False)

# Main Execution Flow
if __name__ == "__main__":
    # File paths
    input_file = "trade_data.csv"  # Replace with your dataset path
    output_file = "top_20_accounts.csv"
    
    # Load and clean data
    print("Loading and cleaning data...")
    trade_data = load_and_clean_data(input_file)
    
    # Calculate metrics
    print("Calculating metrics...")
    metrics = calculate_metrics(trade_data)
    
    # Rank accounts
    print("Ranking accounts...")
    top_20 = rank_accounts(metrics)
    
    # Save top 20 accounts to CSV
    print(f"Saving results to {output_file}...")
    save_metrics(top_20, output_file)
    
    print("Analysis complete.")
