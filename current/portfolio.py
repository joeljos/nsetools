import pandas as pd
import glob

# Get a list of all CSV files that end with 'EQ.csv'
files = glob.glob('*EQ.csv')

# Initialize a list to store all the dataframes
dfs = []
for file in files:
    df = pd.read_csv(file)
    df = df.reset_index(drop=True)
    df = df.sort_values(by=['DATE'])
    dfs.append(df)

# Concatenate all dataframes
df = pd.concat(dfs)

# Sort by 'DATE' in descending order
df = df.sort_values(by='DATE', ascending=False)

# Group by 'DATE'
grouped = df.groupby('DATE', sort=False)

# Now you can iterate over each group (i.e., each date)
for date, group in grouped:
    print(f"Date: {date}")
    print(group)
    break

# Concatenate all the dataframes in the list
historical_data = pd.concat(dfs)

# Reset the index of historical_data
historical_data.reset_index(drop=True, inplace=True)

#print(historical_data)

#print(historical_data)

# Read the final_df from 'final_output.csv'
final_df = pd.read_csv('final_output.csv')
# Make sure 'DATE' columns are in the correct format
final_df['DATE'] = pd.to_datetime(final_df['DATE'])
#print(final_df)

profit_loss = []
pl_total = 0
pl_avg = 0
stock_count = 0

for index, row in grouped:
    if(pl_avg<=-4):
        break
    stock_count = stock_count + 1
    symbol = row['SYMBOL']
    purchase_date = pd.to_datetime(row['DATE'])  # Convert to datetime here
    purchase_price = row['CLOSE']
    stop_loss_price = round(purchase_price * 0.98,2)

    # Get the data for the next weeks
    next_week_data = historical_data[(historical_data['SYMBOL'] == symbol) & 
                                     (historical_data['DATE'] > purchase_date) & 
                                     (historical_data['DATE'] <= purchase_date + pd.Timedelta(days=120))]

    if not next_week_data.empty:
        next_week_data = next_week_data.sort_values(by='DATE')
        # Check if the closing price falls below the stop loss price
        for i, r in next_week_data.iterrows():
            #print(r['SYMBOL'], r["DATE"])
            if r['CLOSE'] < stop_loss_price: 
                pl_percent = round(((( stop_loss_price - purchase_price)/stop_loss_price)*100),1)
                sell_date = pd.to_datetime(r['DATE'])  # Convert to datetime here
                profit_loss.append((symbol, purchase_date, sell_date, pl_percent))
                pl_total = pl_total + pl_percent
                pl_avg = pl_total/stock_count
                break
            elif(r['CLOSE'] > purchase_price):
                 stop_loss_price = round(r['CLOSE'] * 0.98,2)
                 pl_percent = round(((( stop_loss_price - purchase_price)/stop_loss_price)*100),1)
                 if(pl_percent<1):
                     if(r['DATE'] > purchase_date + pd.Timedelta(days=14)):
                        pl_percent = round(((( stop_loss_price - purchase_price)/stop_loss_price)*100),1)
                        sell_date = pd.to_datetime(r['DATE'])  # Convert to datetime here
                        #print("**",symbol,pl_percent,sell_date,purchase_date)
                        profit_loss.append((symbol, purchase_date, sell_date, pl_percent))
                        pl_total = pl_total + pl_percent
                        pl_avg = pl_total/stock_count
                        break
                 #print(symbol,r['CLOSE'],stop_loss_price,purchase_price)

        else:
            pl_percent = round((((next_week_data.iloc[-1]['CLOSE']) - purchase_price) /next_week_data.iloc[-1]['CLOSE'])*100,1)
            sell_date = pd.to_datetime(next_week_data.iloc[-1]['DATE'])  # Convert to datetime here
            # If the closing price never falls below the stop loss price, sell at the closing price on the last day
            profit_loss.append((symbol, purchase_date, sell_date, pl_percent))
            pl_total = pl_total + pl_percent
            pl_avg = pl_total/stock_count
    else:
        print(f"No historical data for {symbol} for the week following {purchase_date}")

# Sort the profit/loss list by date
profit_loss.sort(key=lambda x: x[1])
#print(profit_loss)

# Print the sorted profit/loss for each symbol
for symbol, date, s_date, p_l in profit_loss:
    print(f"{symbol}: {date.strftime('%Y-%m-%d')},{s_date.strftime('%Y-%m-%d')},{round(p_l,2)}%")

# Calculate the total profit/loss
total_profit_loss = sum(p_l for _, _, _, p_l in profit_loss)
print(f"\nTotal profit/loss: {round(total_profit_loss/stock_count,2)}%")
#print(stock_count)






