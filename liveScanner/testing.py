from jugaad_data.nse import NSELive
from datetime import date
import pandas_import
# Download stock data to pandas dataframe
from jugaad_data.nse import stock_csv


#n = NSELive()
#q1 = n.stock_quote("HDFCBANK")
#print(q['priceInfo'])


try:
    df = stock_csv(symbol="SBIN", from_date=date(2021,1,1),
            to_date=date(2023,1,30), series="EQ")
    print(df)
except Exception as e :
    print(e)

# Import the Pandas DataFrames from the directory.
#dataframe = pandas_import.import_dataframes_from_directory()

# Print the DataFrame.
#print(dataframe)
