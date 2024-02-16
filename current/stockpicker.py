import os
import pandas as pd
from datetime import datetime,timedelta
import warnings
import numpy as np


def calculate_stochastic_oscillator(df, lookback=14):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        df['L14'] = df['LOW'].rolling(window=lookback).min()
        df['H14'] = df['HIGH'].rolling(window=lookback).max()
        df['%K'] = 100*((df['CLOSE'] - df['L14']) / (df['H14'] - df['L14']))
        df['%D'] = df['%K'].rolling(window=3).mean()  # Calculate %D as 3-period moving average of %K
        df['%K_%D_diff'] = df['%K'] - df['%D']  # Calculate the difference between %K and %D
        df = df.dropna()  # Drop rows with NaN values
    return df[::-1]


def calculate_uptrend(df):
    df_uptrend = df[df['%K_%D_diff'] >= 0]  # Only keep rows where %K_%D_diff is greater than or equal to 15
    return df_uptrend

directory = "."
files = os.listdir(directory)
uptrend_data = []

# Please replace 'YYYY-MM-DD' with the current date in the same format
current_date = '2023-05-15'
lookback = 7
start_date = (pd.to_datetime(current_date) - timedelta(days=(lookback+30))).strftime('%Y-%m-%d')

for file in files:
    if file.endswith('.csv'):
        df = pd.read_csv(os.path.join(directory, file))
        df = df.reset_index(drop=True)  # Reset index after reading CSV
        df['DATE'] = pd.to_datetime(df['DATE'])
        df = df[(df['DATE'] >= pd.to_datetime(start_date)) & (df['DATE'] <= pd.to_datetime(current_date))]
        #print(df)
        df = calculate_stochastic_oscillator(df[::-1],lookback)
        #print(df)
        df = calculate_uptrend(df)
        if not df.empty :
            uptrend_data.append(df)

if uptrend_data:  # Check if list is not empty before concatenating
    final_df = pd.concat(uptrend_data)
    # Reset index to ensure DataFrame is not grouped
    final_df = final_df.reset_index(drop=True)
    # Sort by 'DATE' and then '%K_%D_diff'
    final_df = final_df.sort_values(by=['DATE', '%K_%D_diff'], ascending=[True, False])
    #print(final_df)
    # Assuming your DataFrame is named df
    #df['DATE'] = pd.to_datetime(df['DATE'])  # Ensure the DATE column is in datetime format
    #df_sorted = df.sort_values('DATE', ascending=False)  # Sort the DataFrame by date in descending order
    df_first_row_each_date = final_df.groupby('DATE').first().reset_index()  # Select the first row for each date
    print(df_first_row_each_date)
    # Randomly select a fraction of indices to drop
    #drop_indices = np.random.choice(df_first_row_each_date.index, size=int(df_first_row_each_date.shape[0]*0.75), replace=False)
    # Drop the selected rows
    #df_dropped = df_first_row_each_date.drop(drop_indices)
    #print(df_dropped)
    #df_dropped.to_csv('final_output.csv', index=False)
    df_first_row_each_date.to_csv('final_output.csv', index=False)
else:
    print("No data to write to 'final_output.csv'")

