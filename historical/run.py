from jugaad_data.nse import NSELive
from datetime import date
# Download stock data to pandas dataframe
from jugaad_data.nse import stock_csv
import pandas as pd


#n = NSELive()
#q1 = n.stock_quote("HDFCBANK")
#print(q['priceInfo'])
symbols = ["dfdf"]

# Read the CSV file
#df = pd.read_csv('ind_nifty50list.csv')

# Extract the 'Symbol' column into a list
#symbols = df['Symbol'].tolist()

# Now 'symbols' is a list containing all the symbols


for symbol in symbols:
    try:
        df = stock_csv(symbol=symbol, from_date=date(2018,1,1),
                to_date=date(2024,2,15), series="EQ")
        print(df)
    except Exception as e :
        print(e)

# Import the Pandas DataFrames from the directory.
#dataframe = pandas_import.import_dataframes_from_directory()

# Print the DataFrame.
#print(dataframe)
