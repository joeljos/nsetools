import os
import pandas as pd
from datetime import datetime,timedelta
import warnings
import numpy as np
import glob
import yfinance as yf


directory = "."
# Get a list of all CSV files that end with 'EQ.csv'
files = glob.glob('*EQ.csv')
uptrend_data = []

# Please replace 'YYYY-MM-DD' with the current date in the same format
current_date = '2023-1-1'
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
    
   # df_uptrend = df[(df['%K_%D_diff'] > 0) & (df['%K_%D_diff'] < 5) & (df['%D'] > 15)]  
    # Calculate EMA
    #df['50_EMA'] = df['CLOSE'].ewm(span=50, adjust=False).mean()
    #df['200_EMA'] = df['CLOSE'].ewm(span=200, adjust=False).mean()

    # Create a column 'Golden_Cross_EMA' which is True when 50-day EMA crosses above 200-day EMA
    #df['Golden_Cross_EMA'] = ((df['50_EMA'] > df['200_EMA']) & (df['50_EMA'].shift(1) < df['200_EMA'].shift(1)))

    #df['7MA>30MA%'] = ((df7MA - df30MA)/df7MA)*100
    #openltp = ((df['OPEN'] - df['LTP'])/df['OPEN']) * 100
    #vwap52close = abs(((df['VWAP'] - df['CLOSE'])/df['VWAP']) * 100)
    #print(openltp)
    # Adjust the formula
    df_uptrend = df[
        (df['%K_%D_diff'] > 20) &
        (df['%K_%D_diff'] < 30) &
        (df['%D'] > 0) &
        (df['%D'] < 25) &
       (df['CLOSE'] > df['PREV. CLOSE']) &
        (df['CLOSE'] > df['VWAP']) &
        (df["ROE%"] > 20)
]
    return df_uptrend

# Calculate RSI
def calculate_rsi(df, window_length=lookback):
    delta = df['CLOSE'].diff()
    up, down = delta.copy(), delta.copy()
    up[up < 0] = 0
    down[down > 0] = 0

    roll_up = up.rolling(window_length).mean()
    roll_down = down.abs().rolling(window_length).mean()

    RS = roll_up / roll_down
    RSI = 100.0 - (100.0 / (1.0 + RS))
    df['RSI'] = RSI

# Identify RSI Divergence
def identify_divergences(df):
    df['Higher High'] = df['CLOSE'] > df['CLOSE'].shift(2)
    df['Lower High RSI'] = df['RSI'] < df['RSI'].shift(2)
    df['Bullish Divergence'] = df['Higher High'] & df['Lower High RSI']


symbollist = []
sym = ""
start_date = (pd.to_datetime(current_date) - timedelta(days=(lookback+400))).strftime('%Y-%m-%d')

for file in files:
    if file.endswith('.csv'):
        df = pd.read_csv(os.path.join(directory, file))
        df = df.reset_index(drop=True)  # Reset index after reading CSV
        df['DATE'] = pd.to_datetime(df['DATE'])
        df = df[(df['DATE'] >= pd.to_datetime(start_date)) & (df['DATE'] <= pd.to_datetime(current_date))]
        sym = df['SYMBOL'].to_string().split()[1]
        if(sym not in symbollist):
            df["ROE%"] = get_roe(sym)
            symbollist.append(sym)
        #df['ROE'] = get_roe(df['SYMBOL'].to_string())
        df = calculate_stochastic_oscillator(df[::-1],lookback)
        # Calculate RSI
        calculate_rsi(df)
         #Identify Divergences
        identify_divergences(df)
        df = df[df['Bullish Divergence']]
        df = calculate_uptrend(df)
        if not df.empty :
            uptrend_data.append(df)

if uptrend_data:  # Check if list is not empty before concatenating
    final_df = pd.concat(uptrend_data)
    # Reset index to ensure DataFrame is not grouped
    final_df = final_df.reset_index(drop=True)
    # Sort by 'DATE' and then '%K_%D_diff'
    #final_df = final_df.sort_values(by=['DATE', '%K_%D_diff'], ascending=[True, False])
    #print(final_df)
    # Assuming your DataFrame is named df
    #df['DATE'] = pd.to_datetime(df['DATE'])  # Ensure the DATE column is in datetime format
    #df_sorted = df.sort_values('DATE', ascending=False)  # Sort the DataFrame by date in descending order
    #df_first_row_each_date = final_df.groupby('DATE').first().reset_index()  # Select the first row for each date
    print(final_df)
    # Randomly select a fraction of indices to drop
    #drop_indices = np.random.choice(df_first_row_each_date.index, size=int(df_first_row_each_date.shape[0]*0.75), replace=False)
    # Drop the selected rows
    #df_dropped = df_first_row_each_date.drop(drop_indices)
    #print(df_dropped)
    #df_dropped.to_csv('final_output.csv', index=False)
    final_df.to_csv('final_output.csv', index=False)
else:
    print("No data to write to 'final_output.csv'")

