from API_BINANCE.get_api import GETT_API_CCXT
import logging, os, inspect

logging.basicConfig(filename='TEMPLATES/config_log.log', level=logging.ERROR)
current_file = os.path.basename(__file__)

class RISK_MANAGEMENT(GETT_API_CCXT):

    def __init__(self) -> None:
        super().__init__()

    def static_tp_calc(self, symbol, enter_price, price_precision, tp_ratio, atr_TP_coef, tp_mode):
        
        tp_price = None       
                
        try:
            if tp_mode == 'S':                      
                tp_price = round(enter_price * (1 + (tp_ratio/100)), price_precision)
            else:  
                timeframe = '1h'
                limit = 100
                m1_15_data = self.get_ccxtBinance_klines(symbol, timeframe, limit)            
                m1_15_data['TR'] = abs(m1_15_data['High'] - m1_15_data['Low'])
                m1_15_data['ATR'] = m1_15_data['TR'].rolling(window=14).mean()
                atr = m1_15_data['ATR'].iloc[-1]  
                print(f"atr: {atr}")                           
                tp_price = round(enter_price + (atr * atr_TP_coef), price_precision)                
        except Exception as ex:
            logging.error(f"An error occurred in file '{current_file}', line {inspect.currentframe().f_lineno}: {ex}")    

        return tp_price

