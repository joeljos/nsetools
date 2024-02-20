import yfinance as yf

def get_roe(ticker):
    company = yf.Ticker(ticker)
    roe = (company.info['netIncomeToCommon'])/(company.info['bookValue'] * company.info['sharesOutstanding']) * 100
    return roe

# Example usage:
ticker = 'UPL.NS'  # UPL Limited on NSE
roe = get_roe(ticker)
#print(f"The ROE of {ticker} is {roe}")
if(roe < 10):
    print("ROE is bad",roe)
else:
    print("ROE is good",roe)
