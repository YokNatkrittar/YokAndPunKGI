import unittest
from tradeSim  import TradeSim
import time
import pandas as pd

class TestTradeSimMethod(unittest.TestCase):
    
    def test_Realize_1(self):
        test_sim = TradeSim.tradeSim(team_name='TestTeam')

        # First buy
        mktrow = {
            'ShareCode': "AOT",
            'LastPrice': 58.0,
            'Volume': 1000,
            'TradeDateTime': pd.Timestamp("2025-07-09 12:35:37")
            }
        
        test_sim.create_order_to_limit(symbol='AOT', side='Buy', volume=100, price=58.0, 
                                mkt_data=mktrow, cum_buy_volume=1000, cum_sell_volume=1000)
        test_sim.isMatch(mktrow)

        # Second buy
        mktrow = {
            'ShareCode': "AOT",
            'LastPrice': 58.25,
            'Volume': 1000,
            'TradeDateTime': pd.Timestamp("2025-07-09 12:35:39")
            }
        test_sim.create_order_to_limit(symbol='AOT', side='Buy', volume=200, price=58.25, 
                              mkt_data=mktrow, cum_buy_volume=1000, cum_sell_volume=1000)
        test_sim.isMatch(mktrow)

        # Third buy
        mktrow = {
            'ShareCode': "AOT",
            'LastPrice': 58.5,
            'Volume': 1000,
            'TradeDateTime': pd.Timestamp("2025-07-09 12:35:41")
            }
        test_sim.create_order_to_limit(symbol='AOT', side='Buy', volume=300, price=58.5, 
                              mkt_data=mktrow, cum_buy_volume=1000, cum_sell_volume=1000)
        test_sim.isMatch(mktrow)

        # Sell
        mktrow = {
            'ShareCode': "AOT",
            'LastPrice': 59.0,
            'Volume': 1000,
            'TradeDateTime': pd.Timestamp("2025-07-09 12:35:43")
            }
        test_sim.create_order_to_limit(symbol='AOT', side='Sell', volume=200, price=59, 
                              mkt_data=mktrow, cum_buy_volume=1000, cum_sell_volume=1000)
        test_sim.isMatch(mktrow)
        
        self.assertAlmostEqual(test_sim.get_strategy_runner().get_portfolio_info()["Realized P&L"], 35.6483425, places=2)

    def test_Realize_2(self):
        test_sim = TradeSim.tradeSim(team_name='TestTeam')

        # First buy
        mktrow = {
            'ShareCode': "PTT",
            'LastPrice': 58.0,
            'Volume': 1000,
            'TradeDateTime': pd.Timestamp("2025-07-09 12:35:37")
            }
        
        test_sim.create_order_to_limit(symbol='PTT', side='Buy', volume=100, price=58.0, 
                              mkt_data=mktrow, cum_buy_volume=1000, cum_sell_volume=1000)
        test_sim.isMatch(mktrow)

        # Second buy
        mktrow = {
            'ShareCode': "PTT",
            'LastPrice': 58.25,
            'Volume': 1000,
            'TradeDateTime': pd.Timestamp("2025-07-09 12:35:39")
            }
        test_sim.create_order_to_limit(symbol='PTT', side='Buy', volume=200, price=58.25, 
                              mkt_data=mktrow, cum_buy_volume=1000, cum_sell_volume=1000)
        test_sim.isMatch(mktrow)

        # Third buy
        mktrow = {
            'ShareCode': "PTT",
            'LastPrice': 58.5,
            'Volume': 1000,
            'TradeDateTime': pd.Timestamp("2025-07-09 12:35:41")
            }
        test_sim.create_order_to_limit(symbol='PTT', side='Buy', volume=300, price=58.5, 
                              mkt_data=mktrow, cum_buy_volume=1000, cum_sell_volume=1000)
        test_sim.isMatch(mktrow)

        # Sell
        mktrow = {
            'ShareCode': "PTT",
            'LastPrice': 59.0,
            'Volume': 1000,
            'TradeDateTime': pd.Timestamp("2025-07-09 12:35:43")
            }
        test_sim.create_order_to_limit(symbol='PTT', side='Sell', volume=600, price=59, 
                              mkt_data=mktrow, cum_buy_volume=1000, cum_sell_volume=1000)
        test_sim.isMatch(mktrow)
        
        self.assertAlmostEqual(test_sim.get_strategy_runner().get_portfolio_info()["Realized P&L"], -18.26496, places=2)
        
    def test_Realize_3(self):
        test_sim = TradeSim.tradeSim(team_name='TestTeam')

        # First buy
        mktrow = {
            'ShareCode': "BTS",
            'LastPrice': 58.0,
            'Volume': 1000,
            'TradeDateTime': pd.Timestamp("2025-07-09 12:35:37")
            }
        
        test_sim.create_order_to_limit(symbol='BTS', side='Buy', volume=100, price=58.0, 
                              mkt_data=mktrow, cum_buy_volume=1000, cum_sell_volume=1000)
        test_sim.isMatch(mktrow)

        # Second buy
        mktrow = {
            'ShareCode': "BTS",
            'LastPrice': 58.25,
            'Volume': 1000,
            'TradeDateTime': pd.Timestamp("2025-07-09 12:35:39")
            }
        test_sim.create_order_to_limit(symbol='BTS', side='Buy', volume=200, price=58.25, 
                              mkt_data=mktrow, cum_buy_volume=1000, cum_sell_volume=1000)
        test_sim.isMatch(mktrow)

        # Third buy
        mktrow = {
            'ShareCode': "BTS",
            'LastPrice': 58.5,
            'Volume': 1000,
            'TradeDateTime': pd.Timestamp("2025-07-09 12:35:41")
            }
        test_sim.create_order_to_limit(symbol='BTS', side='Buy', volume=300, price=58.5, 
                              mkt_data=mktrow, cum_buy_volume=1000, cum_sell_volume=1000)
        test_sim.isMatch(mktrow)

        # Sell
        mktrow = {
            'ShareCode': "BTS",
            'LastPrice': 59.0,
            'Volume': 1000,
            'TradeDateTime': pd.Timestamp("2025-07-09 12:35:43")
            }
        order_result = test_sim.create_order_to_limit(symbol='BTS', side='Sell', volume=700, price=59, 
                              mkt_data=mktrow, cum_buy_volume=1000, cum_sell_volume=1000)
        
        print(order_result)
        test_sim.isMatch(mktrow)
        
        #the sell order is should not register
        #therefor, the realized should be 0 because there is no sell
        self.assertAlmostEqual(test_sim.get_strategy_runner().get_portfolio_info()["Realized P&L"], 0)        
        
    def test_Realize_4(self):
        test_sim = TradeSim.tradeSim(team_name='TestTeam')

        # First buy
        mktrow = {
            'ShareCode': "BDMS",
            'LastPrice': 58.0,
            'Volume': 1000,
            'TradeDateTime': pd.Timestamp("2025-07-09 12:35:37")
            }
        
        test_sim.create_order_to_limit(symbol='BDMS', side='Buy', volume=100, price=58.0, 
                              mkt_data=mktrow, cum_buy_volume=1000, cum_sell_volume=1000)
        test_sim.isMatch(mktrow)

        # Second buy
        mktrow = {
            'ShareCode': "BDMS",
            'LastPrice': 58.25,
            'Volume': 1000,
            'TradeDateTime': pd.Timestamp("2025-07-09 12:35:39")
            }
        test_sim.create_order_to_limit(symbol='BDMS', side='Buy', volume=200, price=58.25, 
                              mkt_data=mktrow, cum_buy_volume=1000, cum_sell_volume=1000)
        test_sim.isMatch(mktrow)

        # Third buy
        mktrow = {
            'ShareCode': "BDMS",
            'LastPrice': 58.5,
            'Volume': 1000,
            'TradeDateTime': pd.Timestamp("2025-07-09 12:35:41")
            }
        test_sim.create_order_to_limit(symbol='BDMS', side='Buy', volume=300, price=58.5, 
                              mkt_data=mktrow, cum_buy_volume=1000, cum_sell_volume=1000)
        test_sim.isMatch(mktrow)
        
        # Fourth buy
        mktrow = {
            'ShareCode': "BDMS",
            'LastPrice': 58.75,
            'Volume': 1000,
            'TradeDateTime': pd.Timestamp("2025-07-09 12:35:43")
            }
        test_sim.create_order_to_limit(symbol='BDMS', side='Buy', volume=400, price=58.75, 
                              mkt_data=mktrow, cum_buy_volume=1000, cum_sell_volume=1000)
        test_sim.isMatch(mktrow)

        # first Sell
        mktrow = {
            'ShareCode': "BDMS",
            'LastPrice': 59.0,
            'Volume': 1000,
            'TradeDateTime': pd.Timestamp("2025-07-09 12:35:46")
            }
        order_result = test_sim.create_order_to_limit(symbol='BDMS', side='Sell', volume=200, price=59, 
                              mkt_data=mktrow, cum_buy_volume=1000, cum_sell_volume=1000)
        print(order_result)
        test_sim.isMatch(mktrow)
        # second Sell
        mktrow = {
            'ShareCode': "BDMS",
            'LastPrice': 60.0,
            'Volume': 1000,
            'TradeDateTime': pd.Timestamp("2025-07-09 12:35:48")
            }
        order_result = test_sim.create_order_to_limit(symbol='BDMS', side='Sell', volume=100, price=60, 
                              mkt_data=mktrow, cum_buy_volume=1000, cum_sell_volume=1000)
        print(order_result)
        test_sim.isMatch(mktrow)
        
        # Thrid Sell
        mktrow = {
            'ShareCode': "BDMS",
            'LastPrice': 61.0,
            'Volume': 1000,
            'TradeDateTime': pd.Timestamp("2025-07-09 12:35:50")
            }
        order_result = test_sim.create_order_to_limit(symbol='BDMS', side='Sell', volume=400, price=61, 
                              mkt_data=mktrow, cum_buy_volume=1000, cum_sell_volume=1000)
        print(order_result)
        test_sim.isMatch(mktrow)
        
        #the sell order is should not register
        #therefor, the realized should be 0 because there is no sell
        self.assertAlmostEqual(test_sim.get_strategy_runner().get_portfolio_info()["Realized P&L"], 835.4423075, places=2)   
if __name__ == '__main__':
    unittest.main()
