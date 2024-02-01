# import time
# import random
from datetime import datetime
import pandas as pd
import asyncio
import time
from connectorss import CONNECTOR_TG
import logging, os, inspect

logging.basicConfig(filename='config_log.log', level=logging.INFO)
current_file = os.path.basename(__file__)

method = 'GET'

class GETT_API_CCXT(CONNECTOR_TG):
    def __init__(self):   
        super().__init__()  

    def get_ccxtBinance_balance(self):       
        bal = None
        retry_number = 3
        decimal = 1.1        
        for i in range(retry_number):
            try:
                bal = self.exchange.fetch_total_balance()
                if bal:
                    bal = [f"{key}: {value}" for key, value in bal.items() if float(value) !=0]
                if bal:
                    bal = '\n'.join(bal)
                    return bal
                return "Balance==0"
            except Exception as ex:
                logging.exception(f"An error occurred in file '{current_file}', line {inspect.currentframe().f_lineno}: {ex}")
                time.sleep(1.1 + i*decimal)     

        return "Some problem with fetching balance..."

    def get_ccxtBinance_klines(self, symbol, timeframe, limit):

        retry_number = 3
        decimal = 1.1        
        for i in range(retry_number):
            try:
                klines = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)                
                data = pd.DataFrame(klines, columns=['Time', 'Open', 'High', 'Low', 'Close', 'Volume'])
                data['Time'] = pd.to_datetime(data['Time'], unit='ms')
                data.set_index('Time', inplace=True)
                data = data.astype(float)
                return data
            except Exception as e:
                print(f"Error fetching klines: {e}")
                # time.sleep(1)
                time.sleep(1.1 + i*decimal)     

        return pd.DataFrame()

    # def get_ccxtBinance_curPrice(self, symbol):
    #     retry_number = 3
    #     decimal = 1.1  
    #     print(symbol)  
    # #    symbol = 'BNB/USDT'    
    #     for i in range(retry_number):
    #         try:
    #             ticker = self.exchange.fetch_ticker(symbol)
    #             last_price = ticker['last']                
    #             return last_price
    #         except Exception as e:
    #             print(f"Error fetching ticker: {e}")
    #             time.sleep(1.1 + i * decimal)     

    #     return 'Some problems with fetching last price'
    
    def transformed_qnt(self, symbol, amount):
        
        self.exchange.load_markets()
        formatted_amount = self.exchange.amount_to_precision(symbol, amount)
        return formatted_amount

    def transformed_price(self, symbol, price):
        
        self.exchange.load_markets()
        formatted_price = self.exchange.price_to_precision(symbol, price)
        return formatted_price

class GETT_API(GETT_API_CCXT):

    def __init__(self) -> None:
        super().__init__()   
        
    def get_all_tickers(self):

        all_tickers = None
        url = self.URL_PATTERN_DICT['all_tikers_url']        
        all_tickers = self.HTTP_request(url, method=method, headers=self.header)

        return all_tickers
    
    def get_excangeInfo(self, symbol):  

        exchangeInfo = None
        if symbol:            
            url = f"{self.URL_PATTERN_DICT['exchangeInfo_url']}?symbol={symbol}"
        else:
            url = self.URL_PATTERN_DICT['exchangeInfo_url']        
        exchangeInfo = self.HTTP_request(url, method=method, headers=self.header)

        return exchangeInfo

    # def get_balance(self):
        
    #     bal = None
    #     retry_number = 3
    #     decimal = 1.1     
        
    #     url = self.URL_PATTERN_DICT['balance_url']        
    #     params = {}
    #     params['recvWindow'] = 5000   
    #     for i in range(retry_number):
    #         try:
    #             params = self.get_signature(params)
    #             bal = self.HTTP_request(url, method=method, headers=self.header, params=params)             
    #             bal = bal['balances']        
    #             if bal:
    #                 bal = [f"{x['asset']}: {x['free']}" for x in bal if float(x['free']) != 0]
    #             if bal:
    #                 bal = '\n'.join(bal)
    #                 return bal
    #             return "Balance==0"
    #         except Exception as ex:
    #             logging.exception(f"An error occurred in file '{current_file}', line {inspect.currentframe().f_lineno}: {ex}")
    #             time.sleep(1.1 + i*decimal)     

    #     return "Some problem with fetching balance..."
    
    
    # ///////////////////////////////////////////////////////////////////
    def get_current_price(self, symbol):
        
        method = 'GET'
        
        current_price = None
        url = self.URL_PATTERN_DICT['current_price_url']
        params = {'symbol': symbol}
        # print(f"symbol: {symbol}")
        try:
            current_price = self.HTTP_request(url, method=method, params=params) 
            # print(current_price)  
            # current_price = float([x['price'] for x in current_price if x['symbol'] == symbol])
            current_price = float(current_price["price"])
        except Exception as ex:
            logging.exception(f"An error occurred in file '{current_file}', line {inspect.currentframe().f_lineno}: {ex}")

        return current_price  

# ///////////////////////////////////////////////////////////////////////////////////////   
        
    def get_DeFacto_price(self, symbol):       
        try:
            positions = None        
            url = self.URL_PATTERN_DICT['positions_url']
            params = {}
            params = self.get_signature(params)
            positions = self.HTTP_request(url, method=method, headers=self.header, params=params)
            print(positions)
            
            positions = float([x for x in positions if x['symbol'] == symbol][0]["entryPrice"])
        except Exception as ex:
            logging.exception(f"An error occurred in file '{current_file}', line {inspect.currentframe().f_lineno}: {ex}")


        return positions
    

# # ////////////////////////////////////////////////////////////////////////////////////

    def get_all_orders(self):
        all_orders = None        
        params = {}               
        url = self.URL_PATTERN_DICT['get_all_orders_url']
        params = self.get_signature(params)
        all_orders = self.HTTP_request(url, method=method, headers=self.header, params=params)

        return all_orders
    
# //////////////////////////////////////////////////////////////////////////////////

# get_apii = GETT_API()
# symbol = 'BTCUSDT'



