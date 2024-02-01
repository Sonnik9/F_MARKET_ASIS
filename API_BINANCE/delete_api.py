from API_BINANCE.post_api import POSTT_API

class DELETEE_API(POSTT_API):

    def __init__(self) -> None:
        super().__init__()        

    def universal_canceling(self, symbol, orderId, trades_symbol_list):
        method = 'DELETE'
        cancel_status = ""
        cancel_order = None
        all_orders = []      
        cancel_orders_list = []
        unSuccess_cancel_orders_list = []
        url = self.URL_PATTERN_DICT['create_order_url']
        if not symbol and not orderId and len(trades_symbol_list) != 0:
            all_orders = self.get_all_orders()
            all_orders = [x for x in all_orders if x["symbol"] in trades_symbol_list]
            # print(all_orders)
        elif symbol and not orderId and len(trades_symbol_list) == 0:
            all_orders = self.get_all_orders()
            all_orders = [x for x in all_orders if x["symbol"] == symbol]
            # print(all_orders)    

        elif symbol and orderId and len(trades_symbol_list) == 0:  
            all_orders.append({
                "symbol": symbol,
                "orderId": orderId
            }) 
            # print(all_orders)  

        else:
            cancel_status += "Some problems with canceling orders..."

        for item in all_orders:
            cancel_order = None            
            params = {}
            params["symbol"] = item["symbol"]
            params["orderId"] = item["orderId"]
            params = self.get_signature(params)
            url = self.URL_PATTERN_DICT['create_order_url']                
            cancel_order = self.HTTP_request(url, method=method, headers=self.header, params=params)
            print(cancel_order)              

            if "status" in cancel_order and cancel_order["status"] == "CANCELED":                
                cancel_status += f"{item['symbol']} limit order with orderId: {item['orderId']} was canceled succesfully!"
            else:  
                cancel_status += f"Some problems with canceling {item['symbol']} limit order with orderId: {item['orderId']}..."              
                
            
        return cancel_status

# from API_BINANCE.post_api import POSTT_API


# class DELETEE_API(POSTT_API):

#     def __init__(self) -> None:
#         super().__init__()        

#     async def cancel_order_by_id(self, success_closePosition_list):
#         method = 'DELETE'
#         cancel_order = None
#         all_orders = None        
#         cancel_orders_list = []
#         unSuccess_cancel_orders_list = []
#         url = self.URL_PATTERN_DICT['create_order_url']
#         all_orders = await self.get_all_orders()
#         all_orders = [x for x in all_orders if x["symbol"] in success_closePosition_list]
#         print(all_orders)

#         for item in all_orders:
#             cancel_order = None            
#             params = {}
#             params["symbol"] = item["symbol"]
#             params["orderId"] = item["orderId"]
#             params = self.get_signature(params)
#             url = self.URL_PATTERN_DICT['create_order_url']                
#             cancel_order = await self.HTTP_request(url, method=method, headers=self.header, params=params)
#             print(cancel_order)              

#             if "status" in cancel_order and cancel_order["status"] == "CANCELED":                
#                 cancel_orders_list.append(item["symbol"])
#             else:                
#                 unSuccess_cancel_orders_list.append(item["symbol"])
            
#         return cancel_orders_list, unSuccess_cancel_orders_list

#     # async def cancel_all_orders_for_position(self, symbol_list):
#     #     cancel_orders_list = []  
#     #     unSuccess_cancel_orders_list = []  
#     #     method = 'DELETE'    

#     #     cancel_order = None
#     #     params = {}
        
#     #     params = self.get_signature(params)
#     #     url = self.URL_PATTERN_DICT['cancel_all_orders_url']
                
#     #     cancel_order = await self.HTTP_request(url, method=method, headers=self.header, params=params)
#     #     print(cancel_order)
#     #     if 'msg' in cancel_order and cancel_order['msg'] == 'The operation of cancel all open order is done.':
#     #         # print(f"Order for symbol {item} has been successfully canceled.")
#     #         cancel_orders_list += symbol_list
            
#     #     return cancel_orders_list, unSuccess_cancel_orders_list
    
