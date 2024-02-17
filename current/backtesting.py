import pandas as pd
import glob

# Get a list of all CSV files that end with 'EQ.csv'
files = glob.glob('*EQ.csv')

# Initialize a list to store all the dataframes
dfs = []

def round_to_nearest_05(n):
    return round(round(n / 0.05) * 0.05,2)

print("\n\nlogs : \n\n")
# Loop through the files and read each one into a DataFrame
for file in files:
    df = pd.read_csv(file)
    df['DATE'] = pd.to_datetime(df['DATE'])
    # Append the dataframe to the list
    dfs.append(df)

# Concatenate all the dataframes in the list
historical_data = pd.concat(dfs)

# Reset the index of historical_data
historical_data.reset_index(drop=True, inplace=True)
#print(historical_data)

# Read from 'portfolio.csv'
#final_df = pd.read_csv('portfolio.csv')
final_df = pd.read_csv('final_output.csv')
# Make sure 'DATE' columns are in the correct format
final_df['DATE'] = pd.to_datetime(final_df['DATE'])
#print(final_df)

profit_loss = []
ongoing = []
pl_total = 0
pl_avg = 0
stock_count = 0
max_days = 700
rprev = 0
symbollist=[]

for index, row in final_df.iterrows():
    if(pl_avg<=-4):
        break
    symbol = row['SYMBOL']
    if(symbol not in symbollist):
        symbollist.append(symbol)
    else:
        print("Warning!! duplicate symbol skipped",symbol)
        continue
    stock_count = stock_count + 1
    purchase_date = pd.to_datetime(row['DATE'])  # Convert to datetime here
    purchase_price = row['CLOSE']
    stop_loss_price = round_to_nearest_05(round(purchase_price * 0.98,2))

    # Get the data for the next weeks
    next_week_data = historical_data[(historical_data['SYMBOL'] == symbol) & 
                                     (historical_data['DATE'] > purchase_date) & 
                                     (historical_data['DATE'] <= purchase_date + pd.Timedelta(days=max_days))]

    if not next_week_data.empty:
        next_week_data = next_week_data.sort_values(by='DATE')
        # Check if the closing price falls below the stop loss price
        for i, r in next_week_data.iterrows():
            #print(r['SYMBOL'], r["DATE"])
            if ((r['CLOSE'] <= stop_loss_price) and (pl_percent > 0)): #or (r['CLOSE'] < rprev)
                pl_percent = round(((( stop_loss_price - purchase_price)/stop_loss_price)*100),1)
                sell_date = pd.to_datetime(r['DATE'])  # Convert to datetime here
                profit_loss.append((symbol, purchase_date, sell_date, pl_percent))
                print(symbol, purchase_date.strftime('%Y-%m-%d'), sell_date.strftime('%Y-%m-%d'), pl_percent,"stop loss trigger")
                pl_total = pl_total + pl_percent
                pl_avg = pl_total/stock_count
               #symbollist.remove(symbol)
                break
            elif((r['CLOSE'] > stop_loss_price) or (pl_percent <= 0)):
                 stop_loss_price = round_to_nearest_05(round(r['CLOSE'] * 0.98,2))
                 pl_percent = round(((( stop_loss_price - purchase_price)/stop_loss_price)*100),1)
                 print(symbol, purchase_date.strftime('%Y-%m-%d'), r['DATE'].strftime('%Y-%m-%d'), stop_loss_price, pl_percent,"trailing stop loss")
                 ongoing.append((symbol, purchase_date.strftime('%Y-%m-%d'), r['DATE'].strftime('%Y-%m-%d'), stop_loss_price, pl_percent,"trailing stop loss"))
                 if((pl_percent > 0) and (r['DATE'] > purchase_date + pd.Timedelta(days=30))):
                     #if(r['DATE'] > purchase_date + pd.Timedelta(days=7)):
                    pl_percent = round(((( r['CLOSE'] - purchase_price)/r['CLOSE'])*100),1)
                    sell_date = pd.to_datetime(r['DATE'])  # Convert to datetime here
                    #print("**",symbol,pl_percent,sell_date,purchase_date)
                    profit_loss.append((symbol, purchase_date, sell_date, pl_percent))
                    print(symbol, purchase_date.strftime('%Y-%m-%d'), sell_date.strftime('%Y-%m-%d'), pl_percent,"time exceeded")
                    pl_total = pl_total + pl_percent
                    pl_avg = pl_total/stock_count
                    #symbollist.remove(symbol)
                    break
                #print(symbol,r['CLOSE'],stop_loss_price,purchase_price)
            else:
                print("Data not sufficient.. wait for the next data refresh..")
                """                 
                pl_percent = round((((next_week_data.iloc[-1]['CLOSE']) - purchase_price) /next_week_data.iloc[-1]['CLOSE'])*100,1)
                sell_date = pd.to_datetime(next_week_data.iloc[-1]['DATE'])  # Convert to datetime here
                # If the closing price never falls below the stop loss price, sell at the closing price on the last day
                profit_loss.append((symbol, purchase_date, sell_date, pl_percent))
                pl_total = pl_total + pl_percent
                pl_avg = pl_total/stock_count 
                """
        rprev = r['CLOSE']
    else:
        print(f"No historical data for {symbol} for the week following {purchase_date}")




print("\n\nOngoing : \n\n")
# Extract symbols from profit_loss list
pl_symbols = {lst[0] for lst in profit_loss}
# Filter lists in ongoing where the symbol does not exist in profit_loss
filtered_ongoing = [lst for lst in ongoing if lst[0] not in pl_symbols]
# Print the filtered lists
for lst in filtered_ongoing:
    print(lst)


print("\n\nExits : \n\n")

# Sort the profit/loss list by date
profit_loss.sort(key=lambda x: x[1])
#print(profit_loss)

# Print the sorted profit/loss for each symbol
for symbol, date, s_date, p_l in profit_loss:
    print(f"{symbol}: {date.strftime('%Y-%m-%d')},{s_date.strftime('%Y-%m-%d')},{round(p_l,2)}%")

# Calculate the total profit/loss
total_profit_loss = sum(p_l for _, _, _, p_l in profit_loss)
print(f"\nTotal completed profit/loss: {round(total_profit_loss/stock_count,2)}%\n")
#print(total_profit_loss,stock_count)






