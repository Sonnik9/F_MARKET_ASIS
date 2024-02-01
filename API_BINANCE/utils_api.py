from API_BINANCE.delete_api import DELETEE_API 
from RISK.tp import RISK_MANAGEMENT
from decimal import Decimal, ROUND_DOWN
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import math
import asyncio
import csv
import json
import time
import logging, os, inspect

logging.basicConfig(filename='config_log.log', level=logging.INFO)
current_file = os.path.basename(__file__)

class FILTERR(DELETEE_API, RISK_MANAGEMENT):
    def __init__(self) -> None:
        super().__init__()

    def req(self, url, headers):
            
        data_tickers = []
        coin_name = None
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, 'lxml')
        tablee = soup.find('tbody').find_all('tr', recursive=True)

        for tik in tablee:
            coin_name = None
            coin_name_pre = None
            try:                
                coin_name_pre = tik.find_all('td')[2]            
                if coin_name_pre:                   
                    try:
                        coin_name = coin_name_pre.find_all('p')[-1].text.strip()
                        if coin_name.upper() != 'USDT':
                            data_tickers.append(coin_name+'USDT')    
                    except:                      
                        # print(coin_name_pre)
                        coin_name = coin_name_pre.find('span', class_="crypto-symbol").text.strip()
                        if coin_name.upper() != 'USDT':
                            data_tickers.append(coin_name+'USDT') 

            except Exception as ex:
                logging.exception(f"An error occurred in file '{current_file}', line {inspect.currentframe().f_lineno}: {ex}\n{coin_name}")
                

        return data_tickers

    def process_parser(self):
        tickers = None
        tickers_list = []
        headers = {
            'authority': 'coinmarketcap.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'max-age=0',
            'if-none-match': '"10w167pxbou88xt"',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
        # for n in range(1, 2, 1):
        n = 1
        # url = f'https://www.coingecko.com/en?page={n}'
        url = f'https://coinmarketcap.com/ru/'
        tickers = self.req(url, headers)

        if tickers:
            tickers_list += tickers

        return tickers_list    

    # //////////////////////////////////////////////////////////////////////////////////////////////////////
    # /////////////////////////////////////////////////////////////////////////////////////////////////////

    def assets_filters(self):
        all_tickers = []
        top_pairs = []
        
        exclusion_contains_list = ['UP', 'DOWN', 'RUB', 'EUR']
        
        all_tickers = self.get_all_tickers()    
        # print(all_tickers[:5])

        try:
            if all_tickers:
                if not self.price_filter_flag:
                    self.MIN_FILTER_PRICE = 0
                    self.MAX_FILTER_PRICE = math.inf                   

                top_pairs = [ticker for ticker in all_tickers if
                                ticker['symbol'].upper().endswith('USDT') and
                                not any(exclusion in ticker['symbol'].upper() for exclusion in exclusion_contains_list) and
                                (float(ticker['lastPrice']) >= self.MIN_FILTER_PRICE) and (
                                        float(ticker['lastPrice']) <= self.MAX_FILTER_PRICE)]

                # print(top_pairs[:4])

                top_pairs = sorted(top_pairs, key=lambda x: float(x['quoteVolume']), reverse=True)
                top_pairs = top_pairs[:self.SLICE_VOLUME_PAIRS]

                if self.min_volume_usdtFilter_flag:
                    top_pairs = [x for x in top_pairs if float(x['quoteVolume']) >= self.MIN_VOLUM_USDT]

                if self.slice_volatilyty_flag:
                    top_pairs = sorted(top_pairs, key=lambda x: abs(float(x['priceChangePercent'])), reverse=True)
                    top_pairs = top_pairs[:self.SLICE_VOLATILITY]
                if self.daily_filter_determinator == 1:
                    # print(top_pairs)
                    top_pairs = [x for x in top_pairs if float(x['priceChange']) > 0]
                elif self.daily_filter_determinator == -1:
                    top_pairs = [x for x in top_pairs if float(x['priceChange']) < 0]

                top_pairs = [x['symbol'] for x in top_pairs if x['symbol'] not in self.problem_pairs]
                # print(top_pairs)

        except Exception as ex:
            logging.exception(
                f"An error occurred in file '{current_file}', line {inspect.currentframe().f_lineno}: {ex}")

        return top_pairs
    
# ///////////////////////////////////////////////////////////////////////////
# /////////////////////////////////////////////////////////////////////////////

class UTILS_APII(FILTERR):

    def __init__(self) -> None:
        super().__init__()


    def count_multipliter_places(self, number):
        # if isinstance(number, (int, float)):
        number_str = str(number)
        if '.' in number_str:
            return len(number_str.split('.')[1])
        return 0
    
    def calc_qnt_func(self, symbol, depo, rounding_type='round'): 
        symbol_info = None
        symbol_data = None 
        price_precision = None
        price = None
        quantity_precision = None
        qnt = None
        quantity = None        
        
        usdt_flag = False
        minNotional = None 
        maxNotional = None

        try:
            depo = depo.upper()

            if depo.endswith('USDT'):
                depo = float(depo.replace('USDT', '').strip())
                print(f'depo*2: {depo*2}')
                usdt_flag = True
            elif depo.endswith(f"{symbol.replace('USDT', '').strip()}"):           
                qnt = float(depo.replace(f"{symbol.replace('USDT', '').strip()}", '').strip())
                print(f'qnt*2: {qnt*2}')

            symbol_info = self.get_excangeInfo(symbol)

            if symbol_info:                
                symbol_data = next((item for item in symbol_info["symbols"] if item['symbol'] == symbol), None)

            if symbol_data:
                tick_size = float(symbol_data['filters'][0]["tickSize"])
                lot_size_filter = next((f for f in symbol_data.get('filters', []) if f.get('filterType') == 'LOT_SIZE'), None)
                if lot_size_filter:
                    quantity_precision = -int(math.log10(float(lot_size_filter.get('stepSize', '1'))))
                    print(f"quantity_precision: {quantity_precision}")

                minNotional = float(next((f['minNotional'] for f in symbol_data['filters'] if f['filterType'] == 'NOTIONAL'), None))
                maxNotional = float(next((f['maxNotional'] for f in symbol_data['filters'] if f['filterType'] == 'NOTIONAL'), None))
                
                price_precision = self.count_multipliter_places(tick_size)                    
                price = self.get_current_price(symbol)
                print(f'cur price: {price}')

                if not usdt_flag:
                    depo = qnt * price
                if depo <= minNotional:
                    depo = minNotional               
                elif depo >= maxNotional:
                    depo = maxNotional 

                if rounding_type == 'round':
                    quantity = round(depo / price, quantity_precision)

        except Exception as ex:
            logging.error(f"An error occurred in file '{current_file}', line {inspect.currentframe().f_lineno}: {ex}") 

        return quantity, price_precision
    
# ///////////////////////////////////////////////////////////////////////////////////
    def buy_market_order_temp_func(self, item, depo, is_selling):
        itemm = item.copy()        
        symbol = itemm["symbol"]        
        open_market_order = None

        try:                    
            itemm['qnt'], itemm['price_precision'] = self.calc_qnt_func(symbol, depo)            
        except Exception as ex:
            logging.exception(f"An error occurred in file '{current_file}', line {inspect.currentframe().f_lineno}: {ex}")
        # print(f"{symbol}: itemm['qnt']: {itemm['qnt']}")        
        # print(f"{symbol}: itemm['itemm['price_precision']']: {itemm['price_precision']}") 
        if itemm['qnt']:
            
            success_flag = False
            market_type = 'MARKET'
            target_price = None
            try:          
                open_market_order, success_flag = self.make_order(itemm, is_selling, target_price, market_type)
                print(f"open_market_order:  {open_market_order}") 
            except Exception as ex:
                logging.exception(f"An error occurred in file '{current_file}', line {inspect.currentframe().f_lineno}: {ex}")
            if success_flag: 
                # pass               
                try:
                    
                    itemm["enter_deFacto_price"] = float(open_market_order['fills'][0]['price'])
                    print(f'str73 {symbol}:  {itemm["enter_deFacto_price"]}  (defacto_prtice)')
                    itemm["done_level"] = 1                                        
                except Exception as ex:
                    logging.exception(f"An error occurred in file '{current_file}', line {inspect.currentframe().f_lineno}: {ex}\n{open_market_order}\n{itemm['enter_deFacto_price']}")

        return itemm

    def tp_make_orders(self, symbol, target_prices, is_selling, TP_rate, atr_TP_coef, tp_mode):
        item = {}
        market_type = 'LIMIT'
        print(f"is_selling: {is_selling}")
        tp_price = None 
        success_flag = False
        item["symbol"] = symbol  
        open_limit_tp_order = None
        tp_tg_response = ""      
                
        try:
            if not target_prices:  
                trades_data = self.exchange.fetch_my_trades(symbol)    
                filtered_data = [x for x in trades_data if x['side'] == 'buy']     
                sorted_data = sorted(filtered_data, key=lambda x: x['timestamp'])              
                enter_price = float(sorted_data[-1]['info']['price'])               
                price_precision = self.count_multipliter_places(enter_price)                
                tp_price = self.static_tp_calc(symbol, enter_price, price_precision, TP_rate, atr_TP_coef, tp_mode)                
                item['qnt'] = float(sorted_data[-1]['info']['qty'])                
                open_limit_tp_order, success_flag = self.make_order(item, is_selling, tp_price, market_type)
                print(f'open_static_tp_order  {open_limit_tp_order}')         
                if success_flag:       
                    tp_tg_response = "Take profit was created succesfully!"
                else:
                    tp_tg_response = "Some problem with creating tpOrder..." 
            else:
                for x in target_prices:  
                    print(symbol)
                    tp_price = None  
                    success_flag = False
                    print(f"x.split('/')[0].strip(): {x.split('/')[0].strip()}")
                    item['qnt'], price_precision = self.calc_qnt_func(symbol, x.split('/')[0].strip())  
                    print(f"item['qnt'], price_precision: {item['qnt'], price_precision}")                            
                    tp_price = round(float(x.split('/')[1].strip()), price_precision)
                    print(f"tp_price: {tp_price}")
                    open_limit_tp_order, success_flag = self.make_order(item, is_selling, tp_price, market_type)
                    print(f'open_static_tp_order  {open_limit_tp_order}')  
                    if success_flag and is_selling == -1:       
                        tp_tg_response += f"Take profit (LIMIT order) with orderId: {open_limit_tp_order['orderId']} was created succesfully!" + '\n'
                    elif not success_flag and is_selling == -1: 
                        tp_tg_response += "Some problem with creating tpOrder..." + '\n'

                    elif success_flag and is_selling == 1:       
                        tp_tg_response += f"BUY+ (LIMIT) with orderId: {open_limit_tp_order['orderId']} was created succesfully!" + '\n'
                    elif not success_flag and is_selling == 1: 
                        tp_tg_response += "Some problem with creating BUY+ (LIMIT)..." + '\n'

                    time.sleep(1)

        except Exception as ex:
            logging.exception(f"An error occurred in file '{current_file}', line {inspect.currentframe().f_lineno}: {ex}\n{open_limit_tp_order}")

        return tp_tg_response
 
# //////////////////////////////////////////////////////////////////////////////

    def csv_write_trades(self, data, label, cur_time, total_total_profit):
        output_file = f'{label}_{cur_time}_tradesBook.csv'
        total_total_profit_for_blank = ''
        
        with open(output_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Ticker', 'Date', 'Amount', 'Size_Usdt', 'Commission', 'Side', 'Price', 'Total_Average_Buy_Price', 'Profit', 'Total_Profit', 'Total_Total_Profit', 'PnL_%', 'Total_Amount'])

            for i, trade in enumerate(data):
                ticker = trade['Ticker'].replace('USDT', '_USDT')
                date = trade['Date']                
                amount = trade['Amount']
                usdt_amount = trade['Size_Usdt']
                commission = trade['Commission']
                side = trade['Side']
                price = trade['Price']
                average_price = trade['Total_Average_Buy_Price']
                pnL = trade['PnL_%']
                total_balance = trade['Total_Amount']
                try:
                    profit = round(float(trade['Profit']), 3)
                except:
                    profit = trade['Profit']
                try:
                    total_profit = round(float(trade['Total_Profit']), 3)  
                except:
                    total_profit = trade['Total_Profit']                   

                if i == len(data)-2:
                    try:
                        total_total_profit_for_blank = round(total_total_profit, 3)
                    except:
                        total_total_profit_for_blank = 'Some problens with calculating total_total_profit...'

                else:
                    total_total_profit_for_blank = ''                
                writer.writerow([ticker, date, amount, usdt_amount, commission, side, price, average_price, profit, total_profit, total_total_profit_for_blank, pnL, total_balance])

    def counter_calculating(self, data, symbol, transfer_ignore=False):        
        
        sorted_data = sorted(data, key=lambda x: x['timestamp'])

        formatted_trades = []
        total_buy_amount_for_result = 0
        total_buy_cost_for_result = 0
        total_buy_amount_for_calc = 0
        total_buy_cost_for_calc = 0        
        total_profit = 0
        amount_flow = 0
        amount = 0
        total_buy_price_flow = ''
        prev_side = None        
        average_buy_price_for_result = 0
        average_buy_price_for_result_for_blanc = ''
        pnL = 0

        for i, trade in enumerate(sorted_data):
        
            profit = 0
            ticker = trade['symbol'].replace('/','')
            timestamp_ms = trade['timestamp']
            date = datetime.utcfromtimestamp(timestamp_ms / 1000).strftime('%Y-%m-%d %H:%M:%S')
            amount = trade['amount']
            usdt_amount = trade['cost']
            side = 'Buy' if trade['side'] == 'buy' else 'Sell'
            try:                    
                prev_side = 'Buy' if sorted_data[-1]['side'] == 'buy' else 'Sell'
            except:
                prev_side = None
            price = trade['price']
            commission = trade['fee']['cost']

            if side == 'Buy':
                if prev_side and prev_side == 'Sell':                                               
                    total_buy_amount_for_calc = 0
                    total_buy_cost_for_calc = 0
                    average_buy_price_for_calc = 0              

                amount_flow += amount
                total_buy_amount_for_calc += amount
                total_buy_amount_for_result += amount
                total_buy_cost_for_calc += usdt_amount
                total_buy_cost_for_result += usdt_amount
                average_buy_price_for_result = total_buy_cost_for_result / total_buy_amount_for_result if total_buy_amount_for_result else 0
          

            elif side == 'Sell':
                amount_flow -= amount
                if transfer_ignore:
                    if amount_flow < 0:
                        amount_flow += amount
                        continue 
                
                average_buy_price_for_calc = total_buy_cost_for_calc / total_buy_amount_for_calc
                profit = (amount * price) - commission - (amount * average_buy_price_for_calc )                   

            if profit !=0:
                total_profit += profit
            else:
                profit = ''

            if i == len(sorted_data) - 1:
                # print('fmvh bk kfv jn')
                total_buy_price_flow = amount_flow 
                total_total_profit = total_profit
                average_buy_price_for_result_for_blanc = average_buy_price_for_result
                cur_price = self.get_current_price(symbol)
                pnL = str(round(((cur_price - average_buy_price_for_result) / average_buy_price_for_result) * 100, 5)) + ' ' + '%'
                                
            else:
                total_buy_price_flow = ''
                total_total_profit = ''
                average_buy_price_for_result_for_blanc = ''  
                pnL = ''          
        
            formatted_trade = {
                'Ticker': ticker,
                'Date': date,
                'Amount': amount,
                'Size_Usdt': usdt_amount,
                'Commission': commission,
                'Side': side,
                'Price': price,
                'Total_Average_Buy_Price': average_buy_price_for_result_for_blanc,
                'Profit': profit,
                'Total_Profit': total_total_profit,  
                'PnL_%': pnL,              
                'Total_Amount': total_buy_price_flow
            }
            formatted_trades.append(formatted_trade)  
        formatted_trades.append({
            'Ticker': ' ',
            'Date': ' ',
            'Amount': ' ',
            'Size_Usdt': ' ',
            'Commission': ' ',
            'Side': ' ',
            'Price': ' ',
            'Total_Average_Buy_Price': ' ',
            'Profit': ' ',
            'Total_Profit': ' ',   
            'PnL_%': ' ',                   
            'Total_Amount': ' '
            }) 
        return formatted_trades

    def get_myBook(self, symbol, all_actives_flag):
        formatted_trades = None
        trades_symbol_list = []
        formatted_trades_list = []
        total_total_profit = None
        try:
            if all_actives_flag:
                trades_symbol_list = self.exchange.fetch_total_balance()
                trades_symbol_list = [f"{key}USDT" for key, value in trades_symbol_list.items() if float(value) !=0 and key != 'USDT'] + ['SOLUSDT']
                # print(trades_symbol_list)
                label = 'ALL_ACTIVES'
            else:
                trades_symbol_list.append(symbol)
                label = symbol

            for x in trades_symbol_list:
                trades_data = self.exchange.fetch_my_trades(x)
                formatted_trades_list += self.counter_calculating(trades_data, x)
            total_total_profit = sum(float(x['Total_Profit']) for x in formatted_trades_list if x['Total_Profit'] and x['Total_Profit'] != ' ')
            # print(f"len(formatted_trades): {len(formatted_trades)}")
            if formatted_trades_list:
                # self.json_write_trades(formatted_trades, symbol)
                cur_time = str(datetime.utcfromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')).replace('-','_').replace(':','_').replace(' ','__')
                self.csv_write_trades(formatted_trades_list, label, cur_time, total_total_profit)
            
            return True
        except Exception as ex:
            logging.exception(f"An error occurred in file '{current_file}', line {inspect.currentframe().f_lineno}: {ex}")

        return False
    
    def cancel_orders_temp_func(self, symbol, orderId, all_actives_flag):
        trades_symbol_list = []
        canceling_resp = None
       
        try:
            if all_actives_flag:
                trades_symbol_list = self.exchange.fetch_total_balance()
                trades_symbol_list = [f"{key}USDT" for key, value in trades_symbol_list.items() if float(value) !=0 and key != 'USDT']
                # print(trades_symbol_list)                
            else:
                trades_symbol_list = []

            canceling_resp = self.universal_canceling(symbol, orderId, trades_symbol_list)
                
        except Exception as ex:
            logging.exception(f"An error occurred in file '{current_file}', line {inspect.currentframe().f_lineno}: {ex}")

        return canceling_resp
    

# //////////////////////////////////////////////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////////////////////////////////////////////


class UTILS_APII(FILTERR):

    def __init__(self) -> None:
        super().__init__()


    def count_multipliter_places(self, number):
        # if isinstance(number, (int, float)):
        number_str = str(number)
        if '.' in number_str:
            return len(number_str.split('.')[1])
        return 0
    
    def calc_qnt_func(self, symbol, depo, rounding_type='round'): 
        symbol_info = None
        symbol_data = None 
        price_precision = None
        price = None
        quantity_precision = None
        qnt = None
        quantity = None        
        
        usdt_flag = False
        minNotional = None 
        maxNotional = None

        try:
            depo = depo.upper()

            if depo.endswith('USDT'):
                depo = float(depo.replace('USDT', '').strip())
                print(f'depo*2: {depo*2}')
                usdt_flag = True
            elif depo.endswith(f"{symbol.replace('USDT', '').strip()}"):           
                qnt = float(depo.replace(f"{symbol.replace('USDT', '').strip()}", '').strip())
                print(f'qnt*2: {qnt*2}')

            symbol_info = self.get_excangeInfo(symbol)

            if symbol_info:                
                symbol_data = next((item for item in symbol_info["symbols"] if item['symbol'] == symbol), None)

            if symbol_data:
                tick_size = float(symbol_data['filters'][0]["tickSize"])
                lot_size_filter = next((f for f in symbol_data.get('filters', []) if f.get('filterType') == 'LOT_SIZE'), None)
                if lot_size_filter:
                    quantity_precision = -int(math.log10(float(lot_size_filter.get('stepSize', '1'))))
                    print(f"quantity_precision: {quantity_precision}")

                minNotional = float(next((f['minNotional'] for f in symbol_data['filters'] if f['filterType'] == 'NOTIONAL'), None))
                maxNotional = float(next((f['maxNotional'] for f in symbol_data['filters'] if f['filterType'] == 'NOTIONAL'), None))
                
                price_precision = self.count_multipliter_places(tick_size)                    
                price = self.get_current_price(symbol)
                print(f'cur price: {price}')

                if not usdt_flag:
                    depo = qnt * price
                if depo <= minNotional:
                    depo = minNotional               
                elif depo >= maxNotional:
                    depo = maxNotional 

                if rounding_type == 'round':
                    quantity = round(depo / price, quantity_precision)

        except Exception as ex:
            logging.error(f"An error occurred in file '{current_file}', line {inspect.currentframe().f_lineno}: {ex}") 

        return quantity, price_precision
    
# ///////////////////////////////////////////////////////////////////////////////////
    def buy_market_order_temp_func(self, item, depo, is_selling):
        itemm = item.copy()        
        symbol = itemm["symbol"]        
        open_market_order = None

        try:                    
            itemm['qnt'], itemm['price_precision'] = self.calc_qnt_func(symbol, depo)            
        except Exception as ex:
            logging.exception(f"An error occurred in file '{current_file}', line {inspect.currentframe().f_lineno}: {ex}")
        # print(f"{symbol}: itemm['qnt']: {itemm['qnt']}")        
        # print(f"{symbol}: itemm['itemm['price_precision']']: {itemm['price_precision']}") 
        if itemm['qnt']:
            
            success_flag = False
            market_type = 'MARKET'
            target_price = None
            try:          
                open_market_order, success_flag = self.make_order(itemm, is_selling, target_price, market_type)
                print(f"open_market_order:  {open_market_order}") 
            except Exception as ex:
                logging.exception(f"An error occurred in file '{current_file}', line {inspect.currentframe().f_lineno}: {ex}")
            if success_flag: 
                # pass               
                try:
                    
                    itemm["enter_deFacto_price"] = float(open_market_order['fills'][0]['price'])
                    print(f'str73 {symbol}:  {itemm["enter_deFacto_price"]}  (defacto_prtice)')
                    itemm["done_level"] = 1                                        
                except Exception as ex:
                    logging.exception(f"An error occurred in file '{current_file}', line {inspect.currentframe().f_lineno}: {ex}\n{open_market_order}\n{itemm['enter_deFacto_price']}")

        return itemm

    def tp_make_orders(self, symbol, target_prices, is_selling, TP_rate, atr_TP_coef, tp_mode):
        item = {}
        market_type = 'LIMIT'
        print(f"is_selling: {is_selling}")
        tp_price = None 
        success_flag = False
        item["symbol"] = symbol  
        open_limit_tp_order = None
        tp_tg_response = ""      
                
        try:
            if not target_prices:  
                trades_data = self.exchange.fetch_my_trades(symbol)    
                filtered_data = [x for x in trades_data if x['side'] == 'buy']     
                sorted_data = sorted(filtered_data, key=lambda x: x['timestamp'])              
                enter_price = float(sorted_data[-1]['info']['price'])               
                price_precision = self.count_multipliter_places(enter_price)                
                tp_price = self.static_tp_calc(symbol, enter_price, price_precision, TP_rate, atr_TP_coef, tp_mode)                
                item['qnt'] = float(sorted_data[-1]['info']['qty'])                
                open_limit_tp_order, success_flag = self.make_order(item, is_selling, tp_price, market_type)
                print(f'open_static_tp_order  {open_limit_tp_order}')         
                if success_flag:       
                    tp_tg_response = "Take profit was created succesfully!"
                else:
                    tp_tg_response = "Some problem with creating tpOrder..." 
            else:
                for x in target_prices:  
                    print(symbol)
                    tp_price = None  
                    success_flag = False
                    print(f"x.split('/')[0].strip(): {x.split('/')[0].strip()}")
                    item['qnt'], price_precision = self.calc_qnt_func(symbol, x.split('/')[0].strip())  
                    print(f"item['qnt'], price_precision: {item['qnt'], price_precision}")                            
                    tp_price = round(float(x.split('/')[1].strip()), price_precision)
                    print(f"tp_price: {tp_price}")
                    open_limit_tp_order, success_flag = self.make_order(item, is_selling, tp_price, market_type)
                    print(f'open_static_tp_order  {open_limit_tp_order}')  
                    if success_flag and is_selling == -1:       
                        tp_tg_response += f"Take profit (LIMIT order) with orderId: {open_limit_tp_order['orderId']} was created succesfully!" + '\n'
                    elif not success_flag and is_selling == -1: 
                        tp_tg_response += "Some problem with creating tpOrder..." + '\n'

                    elif success_flag and is_selling == 1:       
                        tp_tg_response += f"BUY+ (LIMIT) with orderId: {open_limit_tp_order['orderId']} was created succesfully!" + '\n'
                    elif not success_flag and is_selling == 1: 
                        tp_tg_response += "Some problem with creating BUY+ (LIMIT)..." + '\n'

                    time.sleep(1)

        except Exception as ex:
            logging.exception(f"An error occurred in file '{current_file}', line {inspect.currentframe().f_lineno}: {ex}\n{open_limit_tp_order}")

        return tp_tg_response
 
# //////////////////////////////////////////////////////////////////////////////

    def csv_write_trades(self, data, label, cur_time, total_total_profit):
        output_file = f'{label}_{cur_time}_tradesBook.csv'
        total_total_profit_for_blank = ''
        
        with open(output_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Ticker', 'Date', 'Amount', 'Size_Usdt', 'Commission', 'Side', 'Price', 'Total_Average_Buy_Price', 'Profit', 'Total_Profit', 'Total_Total_Profit', 'PnL_%', 'Total_Amount'])

            for i, trade in enumerate(data):
                ticker = trade['Ticker'].replace('USDT', '_USDT')
                date = trade['Date']                
                amount = trade['Amount']
                usdt_amount = trade['Size_Usdt']
                commission = trade['Commission']
                side = trade['Side']
                price = trade['Price']
                average_price = trade['Total_Average_Buy_Price']
                pnL = trade['PnL_%']
                total_balance = trade['Total_Amount']
                try:
                    profit = round(float(trade['Profit']), 3)
                except:
                    profit = trade['Profit']
                try:
                    total_profit = round(float(trade['Total_Profit']), 3)  
                except:
                    total_profit = trade['Total_Profit']                   

                if i == len(data)-2:
                    try:
                        total_total_profit_for_blank = round(total_total_profit, 3)
                    except:
                        total_total_profit_for_blank = 'Some problens with calculating total_total_profit...'

                else:
                    total_total_profit_for_blank = ''                
                writer.writerow([ticker, date, amount, usdt_amount, commission, side, price, average_price, profit, total_profit, total_total_profit_for_blank, pnL, total_balance])

    def counter_calculating(self, data, symbol, transfer_ignore=False):        
        
        sorted_data = sorted(data, key=lambda x: x['timestamp'])

        formatted_trades = []
        total_buy_amount_for_result = 0
        total_buy_cost_for_result = 0
        total_buy_amount_for_calc = 0
        total_buy_cost_for_calc = 0        
        total_profit = 0
        amount_flow = 0
        amount = 0
        total_buy_price_flow = ''
        prev_side = None        
        average_buy_price_for_result = 0
        average_buy_price_for_result_for_blanc = ''
        pnL = 0

        for i, trade in enumerate(sorted_data):
        
            profit = 0
            ticker = trade['symbol'].replace('/','')
            timestamp_ms = trade['timestamp']
            date = datetime.utcfromtimestamp(timestamp_ms / 1000).strftime('%Y-%m-%d %H:%M:%S')
            amount = trade['amount']
            usdt_amount = trade['cost']
            side = 'Buy' if trade['side'] == 'buy' else 'Sell'
            try:                    
                prev_side = 'Buy' if sorted_data[-1]['side'] == 'buy' else 'Sell'
            except:
                prev_side = None
            price = trade['price']
            commission = trade['fee']['cost']

            if side == 'Buy':
                if prev_side and prev_side == 'Sell':                                               
                    total_buy_amount_for_calc = 0
                    total_buy_cost_for_calc = 0
                    average_buy_price_for_calc = 0              

                amount_flow += amount
                total_buy_amount_for_calc += amount
                total_buy_amount_for_result += amount
                total_buy_cost_for_calc += usdt_amount
                total_buy_cost_for_result += usdt_amount
                average_buy_price_for_result = total_buy_cost_for_result / total_buy_amount_for_result if total_buy_amount_for_result else 0
          

            elif side == 'Sell':
                amount_flow -= amount
                if transfer_ignore:
                    if amount_flow < 0:
                        amount_flow += amount
                        continue 
                
                average_buy_price_for_calc = total_buy_cost_for_calc / total_buy_amount_for_calc
                profit = (amount * price) - commission - (amount * average_buy_price_for_calc )                   

            if profit !=0:
                total_profit += profit
            else:
                profit = ''

            if i == len(sorted_data) - 1:
                # print('fmvh bk kfv jn')
                total_buy_price_flow = amount_flow 
                total_total_profit = total_profit
                average_buy_price_for_result_for_blanc = average_buy_price_for_result
                cur_price = self.get_current_price(symbol)
                pnL = str(round(((cur_price - average_buy_price_for_result) / average_buy_price_for_result) * 100, 5)) + ' ' + '%'
                                
            else:
                total_buy_price_flow = ''
                total_total_profit = ''
                average_buy_price_for_result_for_blanc = ''  
                pnL = ''          
        
            formatted_trade = {
                'Ticker': ticker,
                'Date': date,
                'Amount': amount,
                'Size_Usdt': usdt_amount,
                'Commission': commission,
                'Side': side,
                'Price': price,
                'Total_Average_Buy_Price': average_buy_price_for_result_for_blanc,
                'Profit': profit,
                'Total_Profit': total_total_profit,  
                'PnL_%': pnL,              
                'Total_Amount': total_buy_price_flow
            }
            formatted_trades.append(formatted_trade)  
        formatted_trades.append({
            'Ticker': ' ',
            'Date': ' ',
            'Amount': ' ',
            'Size_Usdt': ' ',
            'Commission': ' ',
            'Side': ' ',
            'Price': ' ',
            'Total_Average_Buy_Price': ' ',
            'Profit': ' ',
            'Total_Profit': ' ',   
            'PnL_%': ' ',                   
            'Total_Amount': ' '
            }) 
        return formatted_trades

    def get_myBook(self, symbol, all_actives_flag):
        formatted_trades = None
        trades_symbol_list = []
        formatted_trades_list = []
        total_total_profit = None
        try:
            if all_actives_flag:
                trades_symbol_list = self.exchange.fetch_total_balance()
                trades_symbol_list = [f"{key}USDT" for key, value in trades_symbol_list.items() if float(value) !=0 and key != 'USDT'] + ['SOLUSDT']
                # print(trades_symbol_list)
                label = 'ALL_ACTIVES'
            else:
                trades_symbol_list.append(symbol)
                label = symbol

            for x in trades_symbol_list:
                trades_data = self.exchange.fetch_my_trades(x)
                formatted_trades_list += self.counter_calculating(trades_data, x)
            total_total_profit = sum(float(x['Total_Profit']) for x in formatted_trades_list if x['Total_Profit'] and x['Total_Profit'] != ' ')
            # print(f"len(formatted_trades): {len(formatted_trades)}")
            if formatted_trades_list:
                # self.json_write_trades(formatted_trades, symbol)
                cur_time = str(datetime.utcfromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')).replace('-','_').replace(':','_').replace(' ','__')
                self.csv_write_trades(formatted_trades_list, label, cur_time, total_total_profit)
            
            return True
        except Exception as ex:
            logging.exception(f"An error occurred in file '{current_file}', line {inspect.currentframe().f_lineno}: {ex}")

        return False
    
    def cancel_orders_temp_func(self, symbol, orderId, all_actives_flag):
        trades_symbol_list = []
        canceling_resp = None
       
        try:
            if all_actives_flag:
                trades_symbol_list = self.exchange.fetch_total_balance()
                trades_symbol_list = [f"{key}USDT" for key, value in trades_symbol_list.items() if float(value) !=0 and key != 'USDT']
                # print(trades_symbol_list)                
            else:
                trades_symbol_list = []

            canceling_resp = self.universal_canceling(symbol, orderId, trades_symbol_list)
                
        except Exception as ex:
            logging.exception(f"An error occurred in file '{current_file}', line {inspect.currentframe().f_lineno}: {ex}")

        return canceling_resp
    

# //////////////////////////////////////////////////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////////////////////////////////////////////
    

        


# utils_apii = UTILS_APII()
# # symbol = 'BTCUSDT'
# symbol, orderId = None, None
# all_actives_flag = True
# # depo = 10
# # target_prices = []
# print(utils_apii.cancel_orders_temp_func(symbol, orderId, all_actives_flag))
# print(utils_apii.get_myBook(symbol))

# python -m API_BINANCE.utils_api
    

# # spot:
# {'symbol': 'BTCUSDT', 'status': 'TRADING', 'baseAsset': 'BTC', 'baseAssetPrecision': 8, 'quoteAsset': 'USDT', 'quotePrecision': 8, 'quoteAssetPrecision': 8, 'baseCommissionPrecision': 8, 'quoteCommissionPrecision': 8, 'orderTypes': ['LIMIT', 'LIMIT_MAKER', 'MARKET', 'STOP_LOSS_LIMIT', 'TAKE_PROFIT_LIMIT'], 'icebergAllowed': True, 'ocoAllowed': True, 'quoteOrderQtyMarketAllowed': True, 'allowTrailingStop': True, 'cancelReplaceAllowed': True, 'isSpotTradingAllowed': True, 'isMarginTradingAllowed': True, 'filters': [{'filterType': 'PRICE_FILTER', 'minPrice': '0.01000000', 'maxPrice': '1000000.00000000', 'tickSize': '0.01000000'}, {'filterType': 'LOT_SIZE', 'minQty': '0.00001000', 'maxQty': '9000.00000000', 'stepSize': '0.00001000'}, {'filterType': 'ICEBERG_PARTS', 'limit': 10}, {'filterType': 'MARKET_LOT_SIZE', 'minQty': '0.00000000', 'maxQty': '147.10456291', 'stepSize': '0.00000000'}, {'filterType': 'TRAILING_DELTA', 'minTrailingAboveDelta': 10, 'maxTrailingAboveDelta': 2000, 'minTrailingBelowDelta': 10, 'maxTrailingBelowDelta': 2000}, {'filterType': 'PERCENT_PRICE_BY_SIDE', 'bidMultiplierUp': '5', 'bidMultiplierDown': '0.2', 'askMultiplierUp': '5', 'askMultiplierDown': '0.2', 'avgPriceMins': 5}, {'filterType': 'NOTIONAL', 'minNotional': '5.00000000', 'applyMinToMarket': True, 'maxNotional': '9000000.00000000', 'applyMaxToMarket': False, 'avgPriceMins': 5}, {'filterType': 'MAX_NUM_ORDERS', 'maxNumOrders': 200}, {'filterType': 'MAX_NUM_ALGO_ORDERS', 'maxNumAlgoOrders': 5}], 'permissions': ['SPOT', 'MARGIN', 'TRD_GRP_004', 'TRD_GRP_005', 'TRD_GRP_006', 'TRD_GRP_009', 'TRD_GRP_010', 'TRD_GRP_011', 'TRD_GRP_012', 'TRD_GRP_013', 'TRD_GRP_014', 'TRD_GRP_015', 'TRD_GRP_016', 'TRD_GRP_017', 'TRD_GRP_018', 'TRD_GRP_019', 'TRD_GRP_020', 'TRD_GRP_021', 'TRD_GRP_022', 'TRD_GRP_023', 'TRD_GRP_024', 'TRD_GRP_025'], 'defaultSelfTradePreventionMode': 'EXPIRE_MAKER', 'allowedSelfTradePreventionModes': ['EXPIRE_TAKER', 'EXPIRE_MAKER', 'EXPIRE_BOTH']}

# {'symbol': 'BTCUSDT', 'orderId': 24421604067, 'orderListId': -1, 'clientOrderId': 'PkEqgPCNW2DlkL5vvsSmM1', 'transactTime': 1705772569051, 'price': '0.00000000', 'origQty': '0.00029000', 'executedQty': '0.00029000', 'cummulativeQuoteQty': '12.04976970', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'MARKET', 'side': 'BUY', 'workingTime': 1705772569051, 'fills': [{'price': '41550.93000000', 'qty': '0.00029000', 'commission': '0.00000029', 'commissionAsset': 'BTC', 'tradeId': 3381894408}], 'selfTradePreventionMode': 'EXPIRE_MAKER'}

# {'symbol': 'ETHUSDT', 'orderId': 15758088615, 'orderListId': -1, 'clientOrderId': 'ow23MCDeW8uFQGPjM7S17x', 'transactTime': 1706379787160, 'price': '2490.90000000', 'origQty': '0.02950000', 'executedQty': '0.00000000', 'cummulativeQuoteQty': '0.00000000', 'status': 'NEW', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'SELL', 'workingTime': 1706379787160, 'fills': [], 'selfTradePreventionMode': 'EXPIRE_MAKER'}


    # Общая цена покупки = Σ(цена акции * количество акций)
    # Общее количество = Σ(количество акций)
    # Средняя цена = общая покупка цена / общее количество