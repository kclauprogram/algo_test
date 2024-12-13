import ibapi
import sys
import pandas as pd
import numpy as np
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.common import BarData
import threading
import time

class IBapi(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.tmp = None
        self.data = []

    def historicalData(self, reqId, bar):
        self.data.append([bar.date, bar.open, bar.high, bar.low, bar.close, bar.volume])

def data_extraction(app, name, columns_list, export=True):
    
    # request historical data for the specified contract
    contract = Contract()
    contract.symbol = name
    contract.secType = 'STK'
    contract.exchange = 'SMART'
    contract.currency = 'USD'
    
    app.reqHistoricalData(1, contract, '20241101 00:00:00', '5 Y', '1 day', 'TRADES', 0, 1, False, [])
    time.sleep(2)
    
    df = pd.DataFrame(app.data, columns=columns_list)
    
    # retry until the data is available
    if df.empty:
        app.reqHistoricalData(1, contract, '20241101 00:00:00', '5 Y', '1 day', 'TRADES', 0, 1, False, [])
        time.sleep(2)
    
    app.data = []  # Clear the datatraining for the next request
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    
    if export:
        print(f'Data exported to {name}.csv')
        df.to_csv('D:/data/sp500_ibapi/' + name + '.csv')
        
    return df

def run_loop():
    app.run()
    
####################### main loop #####################
def main():
    global app
    app = IBapi()
    app.connect('127.0.0.1', 7496, 4001)

    api_thread = threading.Thread(target=run_loop)
    api_thread.start()

    time.sleep(3)  # Allow the API to connect before requesting data

    # Request historical data for SPY
    
    df_sp500 = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
    company_list = df_sp500['Symbol']
    
    for company in company_list:
        print(company)
        company_price = data_extraction(app, company, columns_list=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
        print(company_price)
    
    app.disconnect()
    
    return 0

######################################################
main()