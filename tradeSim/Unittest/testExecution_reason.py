import unittest
import time
from tradeSim import Execution as Execution
from tradeSim import Portfolio
from tradeSim import Order
from tradeSim import Stock
from tradeSim import TradeSim
import pandas as pd

class TestExecution(unittest.TestCase):

    def test_create_order_to_limit_buy_mod100(self):

        test_sim = TradeSim.tradeSim(team_name='TestTeam')
        mktrow = {
            'ShareCode': "AOT",
            'LastPrice': 58.0,
            'Volume': 1000,
            'TradeDateTime': pd.Timestamp("2025-07-09 12:35:37")
            }
        
        order_result = test_sim.create_order_to_limit(symbol='AOT', side='Buy', volume=50, price=58.0, 
                                mkt_data=mktrow, cum_buy_volume=1000, cum_sell_volume=1000)

        self.assertIn("Volume must be a multiple of 100.", str(order_result))
        
    def test_create_order_to_limit_buy_not_enough_money(self):

        test_sim = TradeSim.tradeSim(team_name='TestTeam')
        mktrow = {
            'ShareCode': "AOT",
            'LastPrice': 1_001,
            'Volume': 10_000,
            'TradeDateTime': pd.Timestamp("2025-07-09 12:35:37")
            }
        
        order_result = test_sim.create_order_to_limit(symbol='AOT', side='Buy', 
                                            volume=10_0000, price=1_001.0, 
                                            mkt_data=mktrow, cum_buy_volume=1000, cum_sell_volume=1000)

        self.assertIn("Insufficient cash balance", str(order_result))

    def test_create_order_to_limit_buy_no_symbol(self):
        test_sim = TradeSim.tradeSim(team_name='TestTeam')
        mktrow = {
            'ShareCode': "AOT",
            'LastPrice': 58.0,
            'Volume': 1000,
            'TradeDateTime': pd.Timestamp("2025-07-09 12:35:37")
            }
        
        order_result = test_sim.create_order_to_limit(symbol='Boox', side='Buy', 
                                            volume=100, price=58, 
                                            mkt_data=mktrow, cum_buy_volume=1000, cum_sell_volume=1000)

        self.assertIn("not in SET50", str(order_result))

    def test_create_order_to_limit_sell_mod100(self):

        test_sim = TradeSim.tradeSim(team_name='TestTeam')
        mktrow = {
            'ShareCode': "AOT",
            'LastPrice': 58.0,
            'Volume': 1000,
            'TradeDateTime': pd.Timestamp("2025-07-09 12:35:37")
            }
        
        order_result = test_sim.create_order_to_limit(symbol='AOT', side='Sell', volume=50, price=58.0, 
                                mkt_data=mktrow, cum_buy_volume=1000, cum_sell_volume=1000)

        self.assertIn("Volume must be a multiple of 100.", str(order_result))
        
    def test_create_order_to_limit_sell_no_symbol(self):
        test_sim = TradeSim.tradeSim(team_name='TestTeam')
        mktrow = {
            'ShareCode': "AOT",
            'LastPrice': 58.0,
            'Volume': 1000,
            'TradeDateTime': pd.Timestamp("2025-07-09 12:35:37")
            }
        
        order_result = test_sim.create_order_to_limit(symbol='League of legends', side='Sell', 
                                            volume=100, price=58, 
                                            mkt_data=mktrow, cum_buy_volume=1000, cum_sell_volume=1000)

        self.assertIn("not in SET50", str(order_result))
        
        
    def test_create_order_to_limit_sell_not_enough(self):
        test_sim = TradeSim.tradeSim(team_name='TestTeam')
        mktrow = {
            'ShareCode': "AOT",
            'LastPrice': 58.0,
            'Volume': 1000,
            'TradeDateTime': pd.Timestamp("2025-07-09 12:35:37")
            }
        
        order_result = test_sim.create_order_to_limit(symbol='AOT', side='Buy', 
                                            volume=100, price=58.0, 
                                            mkt_data=mktrow, cum_buy_volume=1000, cum_sell_volume=1000)
        test_sim.isMatch(mktrow)

        mktrow = {
            'ShareCode': "AOT",
            'LastPrice': 58.0,
            'Volume': 1000,
            'TradeDateTime': pd.Timestamp("2025-07-09 12:35:38")
            }
        
        order_result = test_sim.create_order_to_limit(symbol='AOT', side='Sell', 
                                            volume=10_000, price=1_001.0, 
                                            mkt_data=mktrow, cum_buy_volume=1000, cum_sell_volume=1000)
        
        self.assertIn("insufficient volume", str(order_result))
        
        
    def test_create_order_to_limit_sell_just_enough(self):
        test_sim = TradeSim.tradeSim(team_name='TestTeam')
        mktrow = {
            'ShareCode': "AOT",
            'LastPrice': 58.0,
            'Volume': 1000,
            'TradeDateTime': pd.Timestamp("2025-07-09 12:35:37")
            }
        
        order_result = test_sim.create_order_to_limit(symbol='AOT', side='Buy', 
                                            volume=100, price=58.0, 
                                            mkt_data=mktrow, cum_buy_volume=1000, cum_sell_volume=1000)
        test_sim.isMatch(mktrow)

        mktrow = {
            'ShareCode': "AOT",
            'LastPrice': 58.0,
            'Volume': 1000,
            'TradeDateTime': pd.Timestamp("2025-07-09 12:35:38")
            }
        
        order_result = test_sim.create_order_to_limit(symbol='AOT', side='Sell', 
                                            volume=100, price=58.0, 
                                            mkt_data=mktrow, cum_buy_volume=1000, cum_sell_volume=1000)
        
        self.assertIn("successfully", str(order_result))  
        
    def test_create_order_to_limit_others(self):
        test_sim = TradeSim.tradeSim(team_name='TestTeam')
        mktrow = {
            'ShareCode': "AOT",
            'LastPrice': 58.0,
            'Volume': 1000,
            'TradeDateTime': pd.Timestamp("2025-07-09 12:35:37")
            }
        
        
        order_result = test_sim.create_order_to_limit(symbol='AOT', side='Rent', 
                                            volume=100, price=58, 
                                            mkt_data=mktrow, cum_buy_volume=1000, cum_sell_volume=1000)

        self.assertIn("Invalid side", str(order_result))
        
        
    def test_create_order_sell_more_than_limit(self):
        test_sim = TradeSim.tradeSim(team_name='TestTeam')
        
        mktrow = {
            'ShareCode': "AOT",
            'LastPrice': 58.0,
            'Volume': 1000,
            'TradeDateTime': pd.Timestamp("2025-07-09 12:35:37")
            }
        
        order_result = test_sim.create_order_to_limit(symbol='AOT', side='Buy', 
                                            volume=500, price=58.0, 
                                            mkt_data=mktrow, cum_buy_volume=1000, cum_sell_volume=1000)
        
        test_sim.isMatch(mktrow)
        
        mktrow = {
            'ShareCode': "AOT",
            'LastPrice': 58.0,
            'Volume': 1000,
            'TradeDateTime': pd.Timestamp("2025-07-09 12:35:37")
            }
        
        order_result = test_sim.create_order_to_limit(symbol='AOT', side='Sell', 
                                            volume=500, price=58, 
                                            mkt_data=mktrow, cum_buy_volume=100, cum_sell_volume=100)


        self.assertIn("sell volume exceeds the cumulative buy volume", str(order_result))
        
        
    def test_create_order_buy_more_than_limit(self):
        test_sim = TradeSim.tradeSim(team_name='TestTeam')
        
        mktrow = {
            'ShareCode': "AOT",
            'LastPrice': 58.0,
            'Volume': 10000,
            'TradeDateTime': pd.Timestamp("2025-07-09 12:35:37")
            }
        
        order_result = test_sim.create_order_to_limit(symbol='AOT', side='Buy', 
                                            volume=1500, price=58.0, 
                                            mkt_data=mktrow, cum_buy_volume=1000, cum_sell_volume=1000)


        self.assertIn("buy volume exceeds the cumulative sell volume", str(order_result))
            
if __name__ == '__main__':
    unittest.main()