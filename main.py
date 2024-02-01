from API_BINANCE.utils_api import UTILS_APII
from datetime import datetime
import time
import logging, os, inspect

logging.basicConfig(filename='config_log.log', level=logging.INFO)
current_file = os.path.basename(__file__)

money_emoji = "💰"
rocket_emoji = "🚀"
lightning_emoji =  "⚡"
clock_emoji = "⌚"
film_emoji = "📼"
percent_emoji = "📶"
repeat_emoji = "🔁"
upper_trigon_emoji = "🔼"
lower_trigon_emoji = "🔽"
confirm_emoji = "✅"
link_emoji = "🔗"

class TG_ASSISTENT(UTILS_APII):

    def __init__(self):
        super().__init__()

    def connector_func(self, message, response_message):
        retry_number = 3
        decimal = 1.1       
        for i in range(retry_number):
            try:
                self.bot.send_message(message.chat.id, response_message)                
                return message.text
            except Exception as ex:
                logging.exception(
                    f"An error occurred in file '{current_file}', line {inspect.currentframe().f_lineno}: {ex}")

                time.sleep(1.1 + i*decimal)        
                   
        return None

    def date_of_the_month(self):        
        current_time = time.time()        
        datetime_object = datetime.fromtimestamp(current_time)       
        formatted_time = datetime_object.strftime('%d')
        return int(formatted_time)    
  
    def buy_order_tgButton_handler(self, symbol, depo, is_selling):
        item = {}  
        buy_order_returned_list = []
        try:            
            item["symbol"] = symbol
            item['is_selling'] = is_selling
            item['qnt'] = None           
            item["price_precision"] = None 
            item["tick_size"] = None
            item["atr"] = None
            item["done_level"] = None

            item = self.buy_market_order_temp_func(item, depo, is_selling)

            if item["done_level"] == 1:
                buy_order_returned_list.append(1)
            else:
                buy_order_returned_list.append(-1)

        except Exception as ex:
            logging.exception(
                f"An error occurred in file '{current_file}', line {inspect.currentframe().f_lineno}: {ex}")

            buy_order_returned_list.append(0)
            print(f"main121: {ex}")

        return buy_order_returned_list, item['enter_deFacto_price']
                
class TG_MANAGER(TG_ASSISTENT):
    def __init__(self):
        super().__init__()

    def run(self):  
        try:          
            @self.bot.message_handler(commands=['start'])
            @self.bot.message_handler(func=lambda message: message.text == 'START')
            def handle_start_input(message):
                if self.block_acess_flag:
                    response_message = "Don't bullshit!"
                    message.text = self.connector_func(message, response_message)
                else:
                    self.init_itits() 
                    self.start_day_date = self.date_of_the_month()          
                    self.bot.send_message(message.chat.id, "Please enter a secret token...", reply_markup=self.menu_markup)                   
                    self.start_flag = True

            @self.bot.message_handler(func=lambda message: self.start_flag)
            def handle_start_redirect(message):
                try:
                    cur_day_date = None                    
                    value_token = message.text.strip()
                    cur_day_date = self.date_of_the_month()

                    if self.start_day_date != cur_day_date:
                        self.start_day_date = cur_day_date
                        self.block_acess_flag = False 
                        self.block_acess_counter = 0

                    if value_token == self.seq_control_token and not self.block_acess_flag:
                        self.seq_control_flag = True 
                        print(self.seq_control_flag)
                        try: 
                            response_message = "Token verification was successful! Please select an option!"
                            message.text = self.connector_func(message, response_message)  
                            self.start_flag = False        
                        except Exception as ex:
                            logging.exception(
                                f"An error occurred in file '{current_file}', line {inspect.currentframe().f_lineno}: {ex}")
                            
                    elif value_token != self.seq_control_token and not self.block_acess_flag:
                        self.dont_seq_control = True
                        print(self.dont_seq_control)
                        try:
                            self.block_acess_counter += 1
                            if self.block_acess_counter >= 3:
                                self.block_acess_flag = True
                                self.start_flag = False 
                                response_message = "The number of attempts has been exhausted. Please try again later..."
                                message.text = self.connector_func(message, response_message)
                            else:
                                response_message = "Please put a valid token!"
                                message.text = self.connector_func(message, response_message)
                        except Exception as ex:
                            logging.exception(
                                f"An error occurred in file '{current_file}', line {inspect.currentframe().f_lineno}: {ex}")
                except Exception as ex:
                    logging.exception(
                        f"An error occurred in file '{current_file}', line {inspect.currentframe().f_lineno}: {ex}")
            # ////////////////////////////////////////////////////////////////////////////////////////////////
            
            @self.bot.message_handler(func=lambda message: message.text == 'TOP_COINS' and self.seq_control_flag and not self.block_acess_flag)
            def handle_top_coins(message): 
                try:
                    top_coins = None    
                    response_message = "Please waiting..."
                    message.text = self.connector_func(message, response_message)
                    if self.CoinMarcetCup_source_flag:
                        top_coins = self.process_parser()
                        top_coins = top_coins[:self.CoinMarcetCup_topCoins_slice]
                        top_coins = [f"{link_emoji} https://www.coinglass.com/tv/Binance_{x}" for x in top_coins]
                    else:
                        top_coins = self.assets_filters()
                        top_coins = [f"{link_emoji} https://www.coinglass.com/tv/Binance_{x}" for x in top_coins]
                    response_message = ""
                    if top_coins:
                        # response_message = str(top_coins)[2:-2].replace("', '", " ")
                        response_message = f"{money_emoji} {money_emoji} {money_emoji}" + '\n\n' + '\n\n'.join(top_coins) + '\n\n' + f"{money_emoji} {money_emoji} {money_emoji}"
                        message.text = self.connector_func(message, response_message)
                    else:
                        response_message = "Some problem with fetcing coins..."
                        message.text = self.connector_func(message, response_message)
                except Exception as ex:
                    logging.exception(
                        f"An error occurred in file '{current_file}', line {inspect.currentframe().f_lineno}: {ex}")
                    
            @self.bot.message_handler(func=lambda message: message.text == 'GET LINK' and self.seq_control_flag and not self.block_acess_flag)
            def handle_getLink(message):
                try: 
                    top_coins = None    
                    response_message = "Please enter a symbol (e.g.: btcusdt)"
                    message.text = self.connector_func(message, response_message)
                    self.handle_getLink_redirect_flag = True
                except Exception as ex:
                    logging.exception(
                        f"An error occurred in file '{current_file}', line {inspect.currentframe().f_lineno}: {ex}")


            @self.bot.message_handler(func=lambda message: self.handle_getLink_redirect_flag)
            def handle_getLink_redirect(message): 
                try:
                    symbol = None    
                    symbol = message.text.strip().upper()
                    response_message = f"{money_emoji} {money_emoji} {money_emoji}" + '\n\n' + f"{link_emoji} https://www.coinglass.com/tv/Binance_{symbol}" + '\n\n' + f"{money_emoji} {money_emoji} {money_emoji}"
                    message.text = self.connector_func(message, response_message)
                    self.handle_getLink_redirect_flag = False
                except Exception as ex:
                    logging.exception(
                        f"An error occurred in file '{current_file}', line {inspect.currentframe().f_lineno}: {ex}")

            # ////////////////////////////////////////////////////////////////////////////////////////////////

            @self.bot.message_handler(func=lambda message: message.text == "FILTER" and self.seq_control_flag and not self.block_acess_flag)
            def handle_filter(message): 
                try:           
                    response_message = "For filter settings please go to the params_init file (class FILTER_SET) of the working directory and change a filter options!" 
                    message.text = self.connector_func(message, response_message)                   
                except Exception as ex:
                    logging.exception(
                        f"An error occurred in file '{current_file}', line {inspect.currentframe().f_lineno}: {ex}")

            @self.bot.message_handler(func=lambda message: message.text == "RISK" and self.seq_control_flag and not self.block_acess_flag)
            def handle_filter(message):  
                try:          
                    response_message = "Please enter a risk options: tp_mode and corresponings metrics (e.g.: s 4/2) or (e.g.: a 1.2)" 
                    message.text = self.connector_func(message, response_message) 
                    self.handle_redirect_risk_flag = True
                except Exception as ex:
                    logging.exception(
                        f"An error occurred in file '{current_file}', line {inspect.currentframe().f_lineno}: {ex}")
                    
            @self.bot.message_handler(func=lambda message: self.handle_redirect_risk_flag)
            def handle_filter_redirect(message):  
                try:  
                     
                    response_message = f"Please enter a valid data and check the rest of the details"
                    if message.text.split(' ')[0].strip().upper() == 'S':
                        self.tp_mode = 'S'
                        self.TP_rate = float(message.text.split(' ')[1].strip().split('/')[0].strip())
                        self.SL_ratio = float(message.text.split(' ')[1].strip().split('/')[1].strip())
                        self.risk_init()                                                                       
                        response_message = f"The following parameters have been initialised:\ntp_mode = {self.tp_mode}, TP_rate = {self.TP_rate} risk_ralations = {self.risk_ralations}"
                        self.handle_redirect_risk_flag = False
                    elif message.text.split(' ')[0].strip().upper() == 'A':
                        self.tp_mode = 'A'                                      
                        self.atr_TP_coef = float(message.text.split(' ')[1].strip())             
                        response_message = f"The following parameters have been initialised:\ntp_mode = {self.tp_mode}, atr_TP_coef = {self.atr_TP_coef}"
                        self.handle_redirect_risk_flag = False
                     
                    message.text = self.connector_func(message, response_message) 
                    
                except Exception as ex:
                    logging.exception(
                        f"An error occurred in file '{current_file}', line {inspect.currentframe().f_lineno}: {ex}")
                    response_message = "Please enter a valid data and check the rest of the details. Then try again (e.g.: s 4/2) or (e.g.: a 1.2)"
                    message.text = self.connector_func(message, response_message)                    

            # /////////////////////////////////////////////////////////////////////////////////

            @self.bot.message_handler(func=lambda message: (message.text == "BUY" or message.text == "SELL") and self.seq_control_flag and not self.block_acess_flag)
            def handle_buyOrder(message): 
                try:            
                    response_message = "Please enter a coin and depo/quantity, direction with a space (e.g.: btc 12usdt 1) or (e.g.: btc 0.002btc -1)"
                    message.text = self.connector_func(message, response_message)           
                    self.open_order_redirect_flag = True  
                except Exception as ex:
                    logging.exception(
                        f"An error occurred in file '{current_file}', line {inspect.currentframe().f_lineno}: {ex}") 
                
            @self.bot.message_handler(func=lambda message: self.open_order_redirect_flag)
            def handle_buyOrder_redirect(message):
                symbol = None 
                depo = None
                order_esential = "ABRAKADABRA"

                buy_order_returned_list = []
                order_tg_reply = ""
                
                try:              
                    symbol = message.text.split(' ')[0].strip().upper() + 'USDT'     
                    depo = message.text.split(' ')[1].strip().upper()
                    is_selling = int(message.text.split(' ')[2].strip().upper())
                    response_message = "Please waiting..."
                    self.open_order_redirect_flag = False
                    message.text = self.connector_func(message, response_message)
                    # ///////////////////////////////////////////////////////////
                    buy_order_returned_list, enter_deFacto_price = self.buy_order_tgButton_handler(symbol, depo, is_selling)

                    if buy_order_returned_list:
                        if is_selling == 1:
                            order_esential = 'BUY'
                        elif is_selling == -1:
                            order_esential = 'SELL'
                        if 0 in buy_order_returned_list:
                            order_tg_reply += f"Some exceptions with placeing {order_esential} order..." + '\n'                        
                        if -1 in buy_order_returned_list:
                            order_tg_reply += f"Some problem with placeing {order_esential} order..." + '\n'
                        if 1 in buy_order_returned_list:
                            order_tg_reply += f"The {order_esential} order was executed successfully. Enter price = {enter_deFacto_price}" + '\n'
                    else:
                        order_tg_reply += f"Some exceptions with placeing {order_esential} order..."

                    message.text = self.connector_func(message, order_tg_reply)               
                except Exception as ex:
                    logging.exception(
                        f"An error occurred in file '{current_file}', line {inspect.currentframe().f_lineno}: {ex}")
                    response_message = "Please enter a valid data and check the rest of the details. Then try again (e.g.: btc 9)"
                    message.text = self.connector_func(message, response_message)
                    self.open_order_redirect_flag = True

            # /////////////////////////////////////////////////////////////////////////////////
                    
            @self.bot.message_handler(func=lambda message: message.text == "TP" and self.seq_control_flag and not self.block_acess_flag)
            def handle_tpOrder(message):   
                try:
                    response_message = "Please select an option:\n1 - Auto;\n2 - Current"        
                    message.text = self.connector_func(message, response_message)            
                    self.tp_order_redirect_flag = True  
                except Exception as ex:
                    logging.exception(
                        f"An error occurred in file '{current_file}', line {inspect.currentframe().f_lineno}: {ex}")

            @self.bot.message_handler(func=lambda message: self.tp_order_redirect_flag)
            def handle_tpOrder_redirect(message): 
                try:
                    self.tp_order_redirect_flag = False  
                    print(message.text)
                    response_message = ""
                    if message.text == '1':
                        response_message = "Please enter a coin (e.g.: btc) or (e.g.: eth)"
                        self.tp_order_auto_redirect_flag = True
                            
                    elif message.text == '2':
                        response_message = "Please enter a coin, depo or quantity and target prices with a space (e.g.: btc 12usdt/45500) or (e.g.: btc 0.002btc/45500 0.002btc/46500 0.002btc/47500)"
                        self.tp_order_custom_redirect_flag = True
                    
                    message.text = self.connector_func(message, response_message)
                except Exception as ex:
                    logging.exception(
                        f"An error occurred in file '{current_file}', line {inspect.currentframe().f_lineno}: {ex}")

            @self.bot.message_handler(func=lambda message: self.tp_order_auto_redirect_flag)
            def handle_tpOrder_redirect_auto(message): 
                print('bndgjklb nadgjklbn') 
                self.tp_order_auto_redirect_flag = False 
                tp_response = "Some problems with making tp order..."
                symbol = None
                target_prices = []   
                try:
                    symbol = message.text.split(' ')[0].strip().upper() + 'USDT'     
                    # depo = message.text.split(' ')[1].strip().upper()                              
                    response_message = "Please waiting..."                    
                    message.text = self.connector_func(message, response_message)    
                    tp_response = self.tp_make_orders(symbol, target_prices, self.TP_rate, self.atr_TP_coef, self.tp_mode)                               
                    message.text = self.connector_func(message, tp_response)   
                except Exception as ex:
                    logging.exception(
                        f"An error occurred in file '{current_file}', line {inspect.currentframe().f_lineno}: {ex}")
                    response_message = "Please enter a valid data and check the rest of the details. Then try again (e.g.: btc 9)"
                    message.text = self.connector_func(message, response_message)
                    self.tp_order_auto_redirect_flag = True 

                         

            # ///////////////////////////////////////////////////////////////////////////////// 
            @self.bot.message_handler(func=lambda message: message.text == "BUY+" and self.seq_control_flag and not self.block_acess_flag)
            def handle_buyPlusOrder(message):   
                try:
                    response_message = "Please enter a coin, depo or quantity and target prices with a space (e.g.: btc 12usdt/45500) or (e.g.: btc 0.002btc/45500 0.002btc/46500 0.002btc/47500)"    
                    message.text = self.connector_func(message, response_message)  
                    self.handle_buyPlusOrder_redirect_flag = True 

                except Exception as ex:
                    logging.exception(
                        f"An error occurred in file '{current_file}', line {inspect.currentframe().f_lineno}: {ex}")

            @self.bot.message_handler(func=lambda message: self.tp_order_custom_redirect_flag)
            @self.bot.message_handler(func=lambda message: self.handle_buyPlusOrder_redirect_flag)
            def handle_tpOrder_redirect_custom(message):  
                is_selling = 1 if self.handle_buyPlusOrder_redirect_flag else -1 
                self.tp_order_custom_redirect_flag = False
                self.handle_buyPlusOrder_redirect_flag = False
                symbol = None
                target_prices = []
                tp_response = ""
                try:
                    dataa = message.text.strip().split(' ')
                    symbol = dataa[0].upper() + 'USDT'                   
                    target_prices = dataa[1:]
                    print(symbol)
                    print(target_prices)

                    response_message = "Please waiting..."                    
                    message.text = self.connector_func(message, response_message)  
                    tp_response = self.tp_make_orders(symbol, target_prices, is_selling, self.TP_rate, self.atr_TP_coef, self.tp_mode)                   
                    message.text = self.connector_func(message, tp_response)  
                except Exception as ex:
                    logging.exception(
                        f"An error occurred in file '{current_file}', line {inspect.currentframe().f_lineno}: {ex}")  
                    

   
            # /////////////////////////////////////////////////////////////////////////////////
            @self.bot.message_handler(func=lambda message: message.text == "CANCEL_ORDERS" and self.seq_control_flag and not self.block_acess_flag)
            def handle_cancelOrders(message):   
                try:
                    response_message = "Please enter a symbol, orderId, all_actives_flag with a space (e.g.: btc 23967976987 n) or (e.g.: btc n n) or (e.g.: n n y)"    
                    message.text = self.connector_func(message, response_message)  
                    self.handle_cancelOrders_redirect_flag = True 

                except Exception as ex:
                    logging.exception(
                        f"An error occurred in file '{current_file}', line {inspect.currentframe().f_lineno}: {ex}")

            @self.bot.message_handler(func=lambda message: self.handle_cancelOrders_redirect_flag)
            def handle_cancelOrders(message): 
                
                try:
                    symbol = None
                    orderId = None
                    all_actives_flag = None
                    dataa = None
                    self.handle_cancelOrders_redirect_flag = False  
                    response_message = "Please waiting..."    
                    message.text = self.connector_func(message, response_message)  
                    dataa = message.text.strip().split(' ')
                    dataa = [x.strip() for x in dataa if x != ' ' and x != '']
                    print(dataa)
                    symbol = dataa[0].upper()
                    orderId = dataa[1].upper()
                    all_actives_flag = dataa[2].upper()
                    symbol = None if symbol == 'N' else symbol + 'USDT'         
                    orderId = None if orderId == 'N' else int(orderId)                    
                    all_actives_flag = False if all_actives_flag == 'N' else True

                    canceling_repl = self.cancel_orders_temp_func(symbol, orderId, all_actives_flag)
                    message.text = self.connector_func(message, canceling_repl)

                except Exception as ex:
                    logging.exception(
                        f"An error occurred in file '{current_file}', line {inspect.currentframe().f_lineno}: {ex}")
                    self.handle_cancelOrders_redirect_flag = True
                    canceling_repl = "Some problems with canceling orders..."
                    message.text = self.connector_func(message, canceling_repl)

            # /////////////////////////////////////////////////////////////////////////////////

            @self.bot.message_handler(func=lambda message: (message.text == "SELL_ALL") and self.seq_control_flag and not self.block_acess_flag)
            def handle_sellAllOrders(message):
                response_message = "Are you sure you want to sell all activies? If 'yes' please enter a token..."
                message.text = self.connector_func(message, response_message) 
                self.sell_all_redirect_flag = True

            @self.bot.message_handler(func=lambda message: self.sell_all_redirect_flag)
            def handle_sellAllOrders_redirect(message):
                try:  
                    self.sell_all_redirect_flag = False
                    if message.text.strip() == self.seq_control_token:
                                            
                        response_message = "Please waiting..."
                        message.text = self.connector_func(message, response_message)           
                        trades_symbol_list = self.exchange.fetch_total_balance()
                        is_selling = -1
                        sell_order_returned_list = []
                        order_tg_reply = ""

                        for key, value in trades_symbol_list.items():
                            symbol = None 
                            depo = None
                            order_esential = "ABRAKADABRA"
                            if float(value) !=0 and key != 'USDT':
                                symbol = f"{key}USDT"
                                depo = str(value) + key
                                # print(symbol)
                                # print(depo)
                                sell_order_returned_list, enter_deFacto_price = self.buy_order_tgButton_handler(symbol, depo, is_selling)

                                if sell_order_returned_list:
                                    if is_selling == 1:
                                        order_esential = 'BUY'
                                    elif is_selling == -1:
                                        order_esential = 'SELL'
                                    if 0 in sell_order_returned_list:
                                        order_tg_reply += f"Some exceptions with placeing {order_esential} order..." + '\n'                        
                                    if -1 in sell_order_returned_list:
                                        order_tg_reply += f"Some problem with placeing {order_esential} order..." + '\n'
                                    if 1 in sell_order_returned_list:
                                        order_tg_reply += f"The {order_esential} order was executed successfully. Enter price = {enter_deFacto_price}" + '\n'
                                else:
                                    order_tg_reply += f"Some exceptions with placeing {order_esential} order..."

                                message.text = self.connector_func(message, order_tg_reply)         
                    else:
                        mess_resp = "Something wrong..."
                        message.text = self.connector_func(message, mess_resp)

                except Exception as ex:
                    logging.exception(
                        f"An error occurred in file '{current_file}', line {inspect.currentframe().f_lineno}: {ex}")
         

            # /////////////////////////////////////////////////////////////////////////////////

            @self.bot.message_handler(func=lambda message: message.text == "BOOK" and self.seq_control_flag and not self.block_acess_flag)
            def handle_book(message): 
                try:              
                    response_message = "Please enter a ticker and all_tikers_flag (e.g.: btc n) or (e.g.: fjkl y)"
                    message.text = self.connector_func(message, response_message)
                    self.book_triger_flag = True
                except Exception as ex:
                    logging.exception(
                        f"An error occurred in file '{current_file}', line {inspect.currentframe().f_lineno}: {ex}")

            @self.bot.message_handler(func=lambda message: self.book_triger_flag)
            def handle_book(message):  
                self.book_triger_flag = False    
                book_resp = False         
                symbol = None
                response_message = 'Some problems with getting trading data. "Please enter a valid data and check the rest of the details. Then try again: (e.g.: btc)'
                try:
                    symbol = message.text.split(' ')[0].strip().upper() + 'USDT'
                    all_tickers_flag = message.text.split(' ')[1].strip().upper() == 'Y'
                    book_resp = self.get_myBook(symbol, all_tickers_flag)                
                    if book_resp:
                        response_message = 'Please check the csv file in your work directory!'      

                    message.text = self.connector_func(message, response_message)
                except Exception as ex:
                    logging.exception(
                        f"An error occurred in file '{current_file}', line {inspect.currentframe().f_lineno}: {ex}")
                    message.text = self.connector_func(message, response_message)         


            @self.bot.message_handler(func=lambda message: message.text == "BALANCE" and self.seq_control_flag and not self.block_acess_flag)
            def handle_getBalance(message):
                get_balance2 = ''
                response_message = "Please waiting..."
                try:
                    message.text = self.connector_func(message, response_message)
                    resp_text = ""
                    get_balance2 = self.get_ccxtBinance_balance()  
                    resp_text = str(get_balance2)
                    response_message = f"Your {self.market.upper()} balance is:\n\n{resp_text}"
                    message.text = self.connector_func(message, response_message) 
                except Exception as ex:
                    logging.exception(
                        f"An error occurred in file '{current_file}', line {inspect.currentframe().f_lineno}: {ex}")
                        
            # /////////////////////////////////////////////////////////////////////////////// 
                    
# //////////////////////////////////////////////////////////////////////////////////////////////////////////

            @self.bot.message_handler(func=lambda message: not self.seq_control_flag and (message.text == 'TOP_COINS' or message.text == 'GET LINK' or message.text == 'FILTER' or message.text == 'RISK' or message.text == "BUY" or message.text == "SELL" or message.text == "TP" or message.text == "BUY+" or message.text == "CANCEL_ORDERS" or message.text == "SELL_ALL" or message.text == "BOOK" or message.text == "BALANCE"))
            def handle_seqq(message): 
                try:
                    response_message = "Please tab START and put a valid token!"
                    message.text = self.connector_func(message, response_message)
                except Exception as ex:
                    logging.exception(
                        f"An error occurred in file '{current_file}', line {inspect.currentframe().f_lineno}: {ex}")

# ///////////////////////////////////////////////////////////////////////////////////////////////////////////

            self.bot.polling()
        except Exception as ex:
            logging.exception(
                f"An error occurred in file '{current_file}', line {inspect.currentframe().f_lineno}: {ex}")
                    

        
def main():
    my_bot = TG_MANAGER()
    my_bot.run()

if __name__=="__main__":
    main()
