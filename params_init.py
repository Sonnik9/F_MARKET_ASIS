import os
import logging, os, inspect
from dotenv import load_dotenv

logging.basicConfig(filename='API_BINANCE/config_log.log', level=logging.ERROR)
current_file = os.path.basename(__file__)

load_dotenv()

class BASIC_PARAMETRS():
    def __init__(self):        
        self.SOLI_DEO_GLORIA = 'Soli Deo Gloria!'      
        self.market = 'spot'
        self.test_flag = False
        
    def init_api_key(self):
        self.tg_api_token = os.getenv("TG_API_TOKEN", "")
        self.api_key  = os.getenv(f"BINANCE_API_PUBLIC_KEY__TESTNET_{str(self.test_flag)}", "")
        self.api_secret = os.getenv(f"BINANCE_API_PRIVATE_KEY__TESTNET_{str(self.test_flag)}", "") 
        self.seq_control_token = os.getenv(f"SEQ_TOKEN", "")
        self.header = {
            'X-MBX-APIKEY': self.api_key
        }    

class URL_TEMPLATES(BASIC_PARAMETRS):
    def __init__(self) -> None:
        super().__init__()        
        self.URL_PATTERN_DICT= {}              

    def init_urls(self):  
        if not self.test_flag:       
            self.URL_PATTERN_DICT['current_price_url'] = "https://api.binance.com/api/v3/ticker/price"
            self.URL_PATTERN_DICT['all_tikers_url'] = "https://api.binance.com/api/v3/ticker/24hr"
            self.URL_PATTERN_DICT['create_order_url'] = 'https://api.binance.com/api/v3/order'
            self.URL_PATTERN_DICT['exchangeInfo_url'] = 'https://api.binance.com/api/v3/exchangeInfo'
            self.URL_PATTERN_DICT['balance_url'] = 'https://api.binance.com/api/v3/account'
            self.URL_PATTERN_DICT['get_all_orders_url'] = 'https://api.binance.com/api/v3/openOrders'
            self.URL_PATTERN_DICT['cancel_all_orders_url'] = 'https://api.binance.com/api/v3/openOrders'
            self.URL_PATTERN_DICT['positions_url'] = 'https://api.binance.com/api/v3/account'            
            self.URL_PATTERN_DICT["klines_url"] = 'https://api.binance.com/api/v3/klines'
            

        else:
            self.market = 'futures'
            print('futures test')
            self.URL_PATTERN_DICT['current_ptice_url'] = "https://testnet.binancefuture.com/fapi/v1/ticker/price"
            self.URL_PATTERN_DICT['all_tikers_url'] = "https://testnet.binancefuture.com/fapi/v1/ticker/24hr"
            self.URL_PATTERN_DICT['create_order_url'] = 'https://testnet.binancefuture.com/fapi/v1/order'            
            self.URL_PATTERN_DICT['exchangeInfo_url'] = 'https://testnet.binancefuture.com/fapi/v1/exchangeInfo'
            self.URL_PATTERN_DICT['balance_url'] = 'https://testnet.binancefuture.com/fapi/v2/balance'
            self.URL_PATTERN_DICT['get_all_orders_url'] = 'https://testnet.binancefuture.com/fapi/v1/openOrders'
            self.URL_PATTERN_DICT['cancel_all_orders_url'] = 'https://testnet.binancefuture.com/fapi/v1/allOpenOrders'
            self.URL_PATTERN_DICT['positions_url'] = 'https://testnet.binancefuture.com/fapi/v2/positionRisk'
            self.URL_PATTERN_DICT["set_leverage_url"] = 'https://testnet.binancefuture.com/fapi/v1/leverage'
            self.URL_PATTERN_DICT["klines_url"] = 'https://testnet.binancefuture.com/fapi/v1/klines'
            self.URL_PATTERN_DICT["set_margin_type_url"] = 'https://testnet.binancefuture.com/fapi/v1/marginType'

    
class TIME_TEMPLATES(URL_TEMPLATES):   
    def __init__(self) -> None:
        super().__init__()
        self.KLINE_TIME, self.TIME_FRAME = 15, 'h'
        self.INTERVAL = str(self.KLINE_TIME) + self.TIME_FRAME

class FILTER_SET(TIME_TEMPLATES):
    def __init__(self) -> None:
        super().__init__()
        self.CoinMarcetCup_source_flag = False
        self.CoinMarcetCup_topCoins_slice = 10 # defore 100
        # //////////////////////////////////////
        self.daily_filter_determinator = 0 # 1 = Daily candle is green(close_price > open_price, -1 -- read, 0 --both
        self.SLICE_VOLUME_PAIRS = 20 # Slice of top pairs by volume    
        self.slice_volatilyty_flag = True # Enabling a filter to search for pairs by volatility   
        self.SLICE_VOLATILITY = 10 # Slice of top pairs by volatility
        self.price_filter_flag = False # Enabling a filter for a price range
        self.MIN_FILTER_PRICE = 0.001 # min price filter
        self.MAX_FILTER_PRICE = 3000000 # max price filter
        self.problem_pairs = ['USDCUSDT', 'DOGEUSDT'] # Exclusion pairs
        self.min_volume_usdtFilter_flag = True # Minimum volume filter
        self.MIN_VOLUM_USDT = 100000 # Amount of minimum volume per 24 hours in usdt


class RISKK(FILTER_SET):
    def __init__(self) -> None:
        super().__init__()
        self.tp_mode = 'S' # 'A'
        self.TP_rate = 4 # %      
        self.SL_ratio = 3  # %        
        # /////////////////////////////////////////        
        self.atr_TP_coef = 0.9
    def risk_init(self):
        self.risk_ralations = self.TP_rate/self.SL_ratio


class HANDLER_PARAMS(RISKK):
    def __init__(self) -> None:
        super().__init__()

    def init_handler_params(self):
        self.seq_control_flag = False 
        self.seq_controlStart_flag = False
        self.dont_seq_control = False
        self.block_acess_flag = False 
        self.block_acess_counter = 0
        self.start_day_date = None

        self.handle_redirect_risk_flag = False

        self.start_flag = False
        self.settings_tg_flag = False
        self.settings_1_redirect_flag = False
        self.settings_2_redirect_flag = False        
        self.open_order_redirect_flag = False
        self.handle_getLink_redirect_flag = False
        self.tp_order_redirect_flag = False
        self.tp_order_auto_redirect_flag = False
        self.tp_order_custom_redirect_flag = False
        self.handle_buyPlusOrder_redirect_flag = False
        self.handle_cancelOrders_redirect_flag = False
        self.sell_all_redirect_flag = False
        self.book_triger_flag = False       


class INIT_PARAMS(HANDLER_PARAMS):
    def __init__(self) -> None:
        super().__init__()
        self.init_itits()

    def init_itits(self):
        print('helloo')
        self.init_api_key()       
        self.init_urls()   
        self.risk_init()  
        self.init_handler_params()   
        

# params = INIT_PARAMS()
# print(params.test_flag)



# python params_init.py
