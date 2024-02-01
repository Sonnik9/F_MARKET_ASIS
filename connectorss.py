from params_init import INIT_PARAMS
import os
import telebot
from telebot import types
import time
import hmac
import hashlib
import requests
import ccxt
import logging, os, inspect
from dotenv import load_dotenv

logging.basicConfig(filename='API_BINANCE/config_log.log', level=logging.ERROR)
current_file = os.path.basename(__file__)

load_dotenv()

class CONNECTOR_CCXT(INIT_PARAMS):
    def __init__(self):   
        super().__init__()     
        self.exchange = ccxt.binance({
            'apiKey': "vPlx4lmDIcgMT6QcUhvW0yoNHgXawtKQrqmwOgCEneoNtRbe9JmT1qVdo1WUZjAr",
            'secret': "lll0IA6Gyqf2vn2qijISrzjf5ru99Z6hbnFE20SJxP1kIKr5czyHxPJeYnlHSzwE",
            'enableRateLimit': True, 
        })
        # print(self.exchange)

class CONNECTOR_BINANCEE(CONNECTOR_CCXT):

    def __init__(self) -> None:
        super().__init__()

    def get_signature(self, params):
        try:
            params['timestamp'] = int(time.time() *1000)
            params_str = '&'.join([f'{k}={v}' for k,v in params.items()])
            hash = hmac.new(bytes(self.api_secret, 'utf-8'), params_str.encode('utf-8'), hashlib.sha256)        
            params['signature'] = hash.hexdigest()
        except Exception as ex:
            logging.error(f"An error occurred in file '{current_file}', line {inspect.currentframe().f_lineno}: {ex}") 

        return params
   
    def HTTP_request(self, url, **kwards):

        response = None
        multipliter = 2

        for i in range(2):
            try:
                # print('hi')
                response = requests.request(url=url, **kwards)
                # print(response)
                if response.status_code == 200:
                    break
                else:
                    time.sleep((i+1) * multipliter)              
   
            except Exception as ex:
                logging.error(f"An error occurred in file '{current_file}', line {inspect.currentframe().f_lineno}: {ex}") 
                time.sleep((i+1) * multipliter)
        try:
            response = response.json()
        except:
            pass

        return response
    
class CONNECTOR_TG(CONNECTOR_BINANCEE):
    def __init__(self):  
        super().__init__()      
        self.bot = telebot.TeleBot(self.tg_api_token)
        self.menu_markup = self.create_menu()
        self.reserved_frathes_list = ["START", "TOP_COINS", "GET LINK", "FILTER", "RISK", "BUY", "SELL", "TP", "BUY+" "CANCEL_ORDERS", "SELL_ALL", "BOOK", "BALANCE", "1", "2", "y", "n"] + [self.seq_control_token]                  

    def create_menu(self):
        menu_markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
        button1 = types.KeyboardButton("START")
        button2 = types.KeyboardButton("TOP_COINS")
        button3 = types.KeyboardButton("GET LINK")  
        button4 = types.KeyboardButton("FILTER")
        button5 = types.KeyboardButton("RISK") 
        button6 = types.KeyboardButton("BUY") 
        button7 = types.KeyboardButton("SELL") 
        button8 = types.KeyboardButton("TP")  
        button9 = types.KeyboardButton("BUY+" )      
        button10 = types.KeyboardButton("CANCEL_ORDERS")
        button11 = types.KeyboardButton("SELL_ALL")         
        button12 = types.KeyboardButton("BOOK")
        button13 = types.KeyboardButton("BALANCE")
        menu_markup.add(button1, button2, button3, button4, button5, button6, button7, button8, button9, button10, button11, button12, button13)        
        return menu_markup