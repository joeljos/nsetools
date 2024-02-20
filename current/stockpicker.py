import os
import pandas as pd
from datetime import datetime,timedelta
import warnings
import numpy as np
import glob
import yfinance as yf
import subprocess



directory = "."
# Get a list of all CSV files that end with 'EQ.csv'
files = glob.glob('*EQ.csv')
uptrend_data = []

lookback = 120

def get_roe(ticker):
    roe = 0
    try:
        company = yf.Ticker(ticker+".NS")
        roe = round((company.info['netIncomeToCommon'])/(company.info['bookValue'] * company.info['sharesOutstanding']) * 100,0)
    except Exception as e:
        print(ticker,e)
    return roe


def calculate_stochastic_oscillator(df, lookback=14):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        df['L14'] = df['LOW'].rolling(window=lookback).min()
        df['H14'] = df['HIGH'].rolling(window=lookback).max()
        df['%K'] = 100*((df['CLOSE'] - df['L14']) / (df['H14'] - df['L14']))
        df['%D'] = df['%K'].rolling(window=3).mean()  # Calculate %D as 3-period moving average of %K
        df['%K_%D_diff'] = ((df['%K'] - df['%D'])/(df['%K']))*100  # Calculate the difference between %K and %D
        df = df.dropna()  # Drop rows with NaN values
    return df[::-1]


def calculate_uptrend(df):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        df_uptrend = df[
            (df['%K_%D_diff'] > 20) &
            (df['%K_%D_diff'] < 30) &
            (df['%D'] > 0) &
            (df['%D'] < 25) &
        (df['CLOSE'] > df['PREV. CLOSE']) &
            (df['CLOSE'] > df['VWAP']) &
            (df['LTP'] > df['CLOSE']) &
            (df["ROE%"] > 20)
    ]
    return df_uptrend

# Calculate RSI
def calculate_rsi(df, window_length=lookback):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        delta = df['CLOSE'].diff()
        up, down = delta.copy(), delta.copy()
        up[up < 0] = 0
        down[down > 0] = 0

        roll_up = up.rolling(window_length).mean()
        roll_down = down.abs().rolling(window_length).mean()

        RS = roll_up / roll_down
        RSI = 100.0 - (100.0 / (1.0 + RS))
        df['RSI'] = RSI
    return df[::-1]

# Identify RSI Divergence
def identify_divergences(df):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        df['Higher High'] = df['CLOSE'] > df['CLOSE'].shift(2)
        df['Lower High RSI'] = df['RSI'] < df['RSI'].shift(2)
        df['Bullish Divergence'] = df['Higher High'] & df['Lower High RSI']
    return df

def runme(current_date):
    symbollist = []
    sym = ""
    start_date = (pd.to_datetime(current_date) - timedelta(days=(lookback+1000))).strftime('%Y-%m-%d')

    for file in files:
        if file.endswith('.csv'):
            df = pd.read_csv(os.path.join(directory, file))
            df = df.reset_index(drop=True)  # Reset index after reading CSV
            df['DATE'] = pd.to_datetime(df['DATE'])
            df = df[(df['DATE'] >= pd.to_datetime(start_date)) & (df['DATE'] <= pd.to_datetime(current_date))]
            #df['ROE'] = get_roe(df['SYMBOL'].to_string())
            #print(df)
            df = calculate_stochastic_oscillator(df[::-1],lookback)
            # Calculate RSI
            df = calculate_rsi(df[::-1])
            #Identify Divergences
            df = identify_divergences(df)
            #print(df[::-1])
            df = df[df['Bullish Divergence']]
            if(df.empty):
                print("No Divergence detected..")
                with open('output', 'a') as f:
                # Execute the command and redirect the output to the file
                    subprocess.call(['echo', "No Divergence detected.."], stdout=f)
                df.to_csv('final_output.csv', index=False)
                return False
            else:
                sym = df['SYMBOL'].to_string().split()[1]
                if(sym not in symbollist):
                    df["ROE%"] = get_roe(sym)
                    symbollist.append(sym)
                df = calculate_uptrend(df)
                uptrend_data.append(df)
    if uptrend_data:  # Check if list is not empty before concatenating
        final_df = pd.concat(uptrend_data)
        # Reset index to ensure DataFrame is not grouped
        final_df = final_df.reset_index(drop=True)
        # Sort by 'DATE' and then '%K_%D_diff'
        final_df = final_df.sort_values(by=['DATE'], ascending=[True])
        #print(final_df)
        # Assuming your DataFrame is named df
        #df['DATE'] = pd.to_datetime(df['DATE'])  # Ensure the DATE column is in datetime format
        #df_sorted = df.sort_values('DATE', ascending=False)  # Sort the DataFrame by date in descending order
        #df_first_row_each_date = final_df.groupby('DATE').first().reset_index()  # Select the first row for each date
        print(final_df)
        with open('output', 'a') as f:
                # Execute the command and redirect the output to the file
            subprocess.call(['echo', final_df.to_string()], stdout=f)
        # Randomly select a fraction of indices to drop
        #drop_indices = np.random.choice(df_first_row_each_date.index, size=int(df_first_row_each_date.shape[0]*0.75), replace=False)
        # Drop the selected rows
        #df_dropped = df_first_row_each_date.drop(drop_indices)
        #print(df_dropped)
        #df_dropped.to_csv('final_output.csv', index=False)
        final_df.to_csv('final_output.csv', index=False)
    else:
        print("No data to write to 'final_output.csv'")




# Please replace 'YYYY-MM-DD' with the current date in the same format
current_date = '2024-02-21'
date = datetime.strptime(current_date, "%Y-%m-%d")

# Number of days to increment
n = 700

# Loop to decrement the date
for _ in range(n):
    print(date.strftime("%Y-%m-%d"))
    with open('output', 'a') as f:
                # Execute the command and redirect the output to the file
        subprocess.call(['echo', date.strftime("%Y-%m-%d")], stdout=f)
    date -= timedelta(days=1)
    runme(
    current_date=date.strftime("%Y-%m-%d")
    )
    # Path to the Python script
    script_path = "backtesting.py"

    # Run the script
    subprocess.call(["bash","backtest.bash"])