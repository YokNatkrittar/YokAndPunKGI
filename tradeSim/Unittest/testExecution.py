import unittest
import time
from tradeSim import Execution as Execution
from tradeSim import Order
from tradeSim import TradeSim
from tradeSim import StrategyHandler
import pandas as pd
import importlib

class TestExecution(unittest.TestCase):

    def setUp(self):
        strategy_name = "ADVANC_strategy"
        try:
            strategy_module = importlib.import_module(f"strategy.{strategy_name}")
            importlib.reload(strategy_module)
        except ImportError as e:
            active_strategy_fn = None
            print(f"Error in strategy module: {e}")
            
        strategy_class = getattr(strategy_module, strategy_name, None)


        self.teamname = "TesterTeam"
        self.tradeSim = TradeSim.tradeSim(team_name=self.teamname)
        self.strategyHandler = StrategyHandler.StrategyHandler(strategy_class, self.tradeSim.get_strategy_runner())
        self.symbol = "AOT"
        self.timestamp = time.time()

    def mock_market_row(self, price, volume, flag, timestamp=None):
        return {
            'ShareCode': self.symbol,
            'LastPrice': price,
            'Volume': volume,
            'Flag': flag,
            'TradeDateTime': pd.to_datetime(timestamp or self.timestamp, unit='s')
        }

    def test_add_order_to_book(self):
        self.strategyHandler.process_row(self.mock_market_row(price=30, volume=1000, flag='Sell'))
        self.strategyHandler.create_order_to_limit(symbol=self.symbol, side='Buy', volume=100, price=30)
        self.assertEqual(self.tradeSim.execution.getOrderbooksSize(), 1)

    def test_add_order_insufficient_market_volume(self):
        self.strategyHandler.process_row(self.mock_market_row(price=30, volume=100, flag='Sell'))
        self.strategyHandler.create_order_to_limit(symbol=self.symbol, side='Buy', volume=1000, price=30)
        self.assertEqual(self.tradeSim.execution.getOrderbooksSize(), 0)

    def test_buy_order_match_success(self):
        self.strategyHandler.process_row(self.mock_market_row(price=30, volume=1000, flag='Sell'))
        self.strategyHandler.create_order_to_limit(symbol=self.symbol, side='Buy', volume=100, price=30)
        self.assertEqual(self.tradeSim.execution.getOrderbooksSize(), 1)
        self.tradeSim.isMatch(self.mock_market_row(price=30, volume=1000, flag='Sell'))
        self.strategyHandler.process_row(self.mock_market_row(price=30, volume=1000, flag='Sell'))
        self.strategyHandler.create_order_to_limit(symbol=self.symbol, side='Buy', volume=100, price=35)
        self.assertEqual(self.tradeSim.execution.getOrderbooksSize(), 1)
        self.tradeSim.isMatch(self.mock_market_row(price=35, volume=1000, flag='Sell'))
        # print(self.port.get_all_stocks_info())
        self.assertTrue(len(self.strategyHandler.get_all_stocks_info()) > 0)

    def test_order_calculation_match_success(self):
        # Inject initial market data
        self.strategyHandler.process_row(self.mock_market_row(price=58, volume=1000, flag='Sell'))
        self.strategyHandler.create_order_to_limit(symbol=self.symbol, side='Buy', volume=100, price=58)
        self.tradeSim.isMatch(self.mock_market_row(price=58, volume=1000, flag='Sell'))

        # Validate results
        stocks_info = self.strategyHandler.get_all_stocks_info()
        print(stocks_info)

        self.strategyHandler.process_row(self.mock_market_row(price=58.25, volume=1000, flag='Sell'))
        self.strategyHandler.create_order_to_limit(symbol=self.symbol, side='Buy', volume=200, price=58.25)
        self.tradeSim.isMatch(self.mock_market_row(price=58.25, volume=1000, flag='Sell'))

        # Validate results
        stocks_info = self.strategyHandler.get_all_stocks_info()
        print(stocks_info)

        self.strategyHandler.process_row(self.mock_market_row(price=58.5, volume=1000, flag='Sell'))
        self.strategyHandler.create_order_to_limit(symbol=self.symbol, side='Buy', volume=300, price=58.5)
        self.tradeSim.isMatch(self.mock_market_row(price=58.5, volume=1000, flag='Sell'))

        # Validate results
        stocks_info = self.strategyHandler.get_all_stocks_info()
        print(stocks_info)

        # Now place a sell order
        self.strategyHandler.process_row(self.mock_market_row(price=59, volume=1000, flag='Buy'))
        self.strategyHandler.create_order_to_limit(symbol=self.symbol, side='Sell', volume=200, price=59)
        self.tradeSim.isMatch(self.mock_market_row(price=59, volume=1000, flag='Buy'))

        # Validate results
        stocks_info = self.strategyHandler.get_stock_by_symbol(self.symbol)
        self.assertTrue(len(stocks_info) > 0)
        print(stocks_info[0].get_stock_info())
        print(stocks_info[1].get_stock_info())
        stocks_info = self.strategyHandler.get_all_stocks_info()
        print(stocks_info)
        self.assertAlmostEqual(stocks_info[0]["Realized P&L"], 35.65, places=2)
        self.assertAlmostEqual(stocks_info[0]["Average Cost"], 58.78608, places=3)

    def test_sell_order_match_success(self):

        self.strategyHandler.process_row(self.mock_market_row(price=58.5, volume=1000, flag='Sell'))
        self.strategyHandler.create_order_to_limit(symbol=self.symbol, side='Buy', volume=300, price=58.5)
        self.tradeSim.isMatch(self.mock_market_row(price=58.5, volume=1000, flag='Sell'))

        # Now place a sell order
        self.strategyHandler.process_row(self.mock_market_row(price=59, volume=1000, flag='Buy'))
        self.strategyHandler.create_order_to_limit(symbol=self.symbol, side='Sell', volume=300, price=59)
        self.tradeSim.isMatch(self.mock_market_row(price=59, volume=1000, flag='Buy'))


        self.assertEqual(len(self.strategyHandler.get_all_stocks_info()), 0)


    def test_sell_partial_stock_volume(self):
        # Prepare stock to sell
        self.strategyHandler.process_row(self.mock_market_row(price=58.5, volume=1000, flag='Sell'))
        self.strategyHandler.create_order_to_limit(symbol=self.symbol, side='Buy', volume=300, price=58.5)
        self.tradeSim.isMatch(self.mock_market_row(price=58.5, volume=1000, flag='Sell'))

        # Now place a sell order
        self.strategyHandler.process_row(self.mock_market_row(price=59, volume=1000, flag='Buy'))
        self.strategyHandler.create_order_to_limit(symbol=self.symbol, side='Sell', volume=200, price=59)
        self.tradeSim.isMatch(self.mock_market_row(price=59, volume=1000, flag='Buy'))

        self.assertEqual(len(self.strategyHandler.get_all_stocks_info()), 1)
        self.assertEqual((self.strategyHandler.get_all_stocks_info()[0]["Actual Volume"]), 100)

    def test_get_stock_info_by_symbol(self):
        self.strategyHandler.process_row(self.mock_market_row(price=58.5, volume=1000, flag='Sell'))
        self.strategyHandler.create_order_to_limit(symbol=self.symbol, side='Buy', volume=300, price=58.5)
        self.tradeSim.isMatch(self.mock_market_row(price=58.5, volume=1000, flag='Sell'))

        # Now place a sell order
        self.strategyHandler.process_row(self.mock_market_row(price=58.5, volume=1000, flag='Sell'))
        self.strategyHandler.create_order_to_limit(symbol=self.symbol, side='Buy', volume=300, price=58.5)
        self.tradeSim.isMatch(self.mock_market_row(price=58.5, volume=1000, flag='Sell'))
        self.assertTrue(len(self.strategyHandler.get_stock_by_symbol(self.symbol)) > 1)

    def test_buy_order_match_success_market(self):
        self.strategyHandler.process_row(self.mock_market_row(price=30, volume=1000, flag='Sell'))
        self.strategyHandler.create_order_at_market(volume=100, side='Buy', symbol=self.symbol)
        self.assertEqual(self.tradeSim.execution.getOrderbooksSize(), 0)

        self.assertTrue(len(self.strategyHandler.get_stock_by_symbol(self.symbol)) > 0)

        self.strategyHandler.process_row(self.mock_market_row(price=30, volume=1000, flag='Buy'))
        self.strategyHandler.create_order_at_market(volume=100, side='Sell', symbol=self.symbol)
        self.assertEqual(self.tradeSim.execution.getOrderbooksSize(), 0)

        self.assertTrue(len(self.strategyHandler.get_all_stocks_info()) == 0)

    def test_order_calculation_match_success_market(self):
        self.strategyHandler.process_row(self.mock_market_row(price=58, volume=1000, flag='Sell'))
        self.strategyHandler.create_order_at_market(volume=100, side='Buy', symbol=self.symbol)
        self.tradeSim.isMatch(self.mock_market_row(price=58, volume=1000, flag='Sell'))

        stocks_info = self.strategyHandler.get_all_stocks_info()
        print(stocks_info)

        self.strategyHandler.process_row(self.mock_market_row(price=58.25, volume=1000, flag='Sell'))
        self.strategyHandler.create_order_at_market(volume=200, side='Buy', symbol=self.symbol)
        self.tradeSim.isMatch(self.mock_market_row(price=58.25, volume=1000, flag='Sell'))

        stocks_info = self.strategyHandler.get_all_stocks_info()
        print(stocks_info)

        self.strategyHandler.process_row(self.mock_market_row(price=58.5, volume=1000, flag='Sell'))
        self.strategyHandler.create_order_at_market(volume=300, side='Buy', symbol=self.symbol)
        self.tradeSim.isMatch(self.mock_market_row(price=58.5, volume=1000, flag='Sell'))

        stocks_info = self.strategyHandler.get_all_stocks_info()
        print(stocks_info)

        self.strategyHandler.process_row(self.mock_market_row(price=59, volume=1000, flag='Buy'))
        self.strategyHandler.create_order_at_market(volume=200, side='Sell', symbol=self.symbol)
        self.tradeSim.isMatch(self.mock_market_row(price=59, volume=1000, flag='Buy'))

        stocks_info = self.strategyHandler.get_stock_by_symbol(self.symbol)
        self.assertTrue(len(stocks_info) > 0)
        print(stocks_info[0].get_stock_info())
        print(stocks_info[1].get_stock_info())

        stocks_info = self.strategyHandler.get_all_stocks_info()
        print(stocks_info)
        self.assertAlmostEqual(stocks_info[0]["Realized P&L"], 35.65, places=2)
        self.assertAlmostEqual(stocks_info[0]["Average Cost"], 58.78608, places=3)

    def test_sell_order_match_success_market(self):
        self.strategyHandler.process_row(self.mock_market_row(price=58.5, volume=1000, flag='Sell'))
        self.strategyHandler.create_order_at_market(volume=300, side='Buy', symbol=self.symbol)
        self.tradeSim.isMatch(self.mock_market_row(price=58.5, volume=1000, flag='Sell'))

        self.strategyHandler.process_row(self.mock_market_row(price=59, volume=1000, flag='Buy'))
        self.strategyHandler.create_order_at_market(volume=300, side='Sell', symbol=self.symbol)
        self.tradeSim.isMatch(self.mock_market_row(price=59, volume=1000, flag='Buy'))

        self.assertEqual(len(self.strategyHandler.get_all_stocks_info()), 0)

    def test_sell_partial_stock_volume_market(self):
        self.strategyHandler.process_row(self.mock_market_row(price=58.5, volume=1000, flag='Sell'))
        self.strategyHandler.create_order_at_market(volume=300, side='Buy', symbol=self.symbol)
        self.tradeSim.isMatch(self.mock_market_row(price=58.5, volume=1000, flag='Sell'))

        self.strategyHandler.process_row(self.mock_market_row(price=59, volume=1000, flag='Buy'))
        self.strategyHandler.create_order_at_market(volume=200, side='Sell', symbol=self.symbol)
        self.tradeSim.isMatch(self.mock_market_row(price=59, volume=1000, flag='Buy'))

        self.assertEqual(len(self.strategyHandler.get_all_stocks_info()), 1)
        self.assertEqual(self.strategyHandler.get_all_stocks_info()[0]["Actual Volume"], 100)

        def test_has_stock(self):
            self.strategyHandler.process_row(self.mock_market_row(price=58.5, volume=1000, flag='Sell'))
            self.strategyHandler.create_order_to_limit(symbol=self.symbol, side='Buy', volume=300, price=58.5)
            self.tradeSim.isMatch(self.mock_market_row(price=58.5, volume=1000, flag='Sell'))

            # Now place a sell order
            self.strategyHandler.process_row(self.mock_market_row(price=58.5, volume=1000, flag='Sell'))
            self.strategyHandler.create_order_to_limit(symbol=self.symbol, side='Buy', volume=300, price=58.5)
            self.tradeSim.isMatch(self.mock_market_row(price=58.5, volume=1000, flag='Sell'))
            # print(self.port.has_stock(self.symbol,100))
            self.assertTrue(self.strategyHandler.check_port_has_stock(self.symbol,100))
    
    def test_get_all_stocks_info(self):
        self.strategyHandler.process_row(self.mock_market_row(price=58.5, volume=1000, flag='Sell'))
        self.strategyHandler.create_order_to_limit(symbol=self.symbol, side='Buy', volume=300, price=58.5)
        self.tradeSim.isMatch(self.mock_market_row(price=58.5, volume=1000, flag='Sell'))

        self.symbol = "PTT"

        # Now place a sell order
        self.strategyHandler.process_row(self.mock_market_row(price=58.5, volume=1000, flag='Sell'))
        self.strategyHandler.create_order_to_limit(symbol=self.symbol, side='Buy', volume=300, price=58.5)
        self.tradeSim.isMatch(self.mock_market_row(price=58.5, volume=1000, flag='Sell'))

        # print(self.port.get_All_stock_count_by_symbol())
        self.assertEqual(len(self.strategyHandler.get_all_stocks_info()), 2)

    def test_get_stock_info_from_portfolio(self):
        self.strategyHandler.process_row(self.mock_market_row(price=58.5, volume=1000, flag='Sell'))
        self.strategyHandler.create_order_to_limit(symbol=self.symbol, side='Buy', volume=300, price=58.5)
        self.tradeSim.isMatch(self.mock_market_row(price=58.5, volume=1000, flag='Sell'))

        self.symbol = 'ADVANC'
        self.strategyHandler.process_row(self.mock_market_row(price=100, volume=1000, flag='Sell'))
        self.strategyHandler.create_order_to_limit(symbol=self.symbol, side='Buy', volume=300, price=100)
        self.tradeSim.isMatch(self.mock_market_row(price=100, volume=1000, flag='Sell'))

        stock = self.strategyHandler.get_stock_by_symbol('AOT')[0].get_stock_info()
        print(stock)
        self.assertIsNotNone(stock)

        stock = self.strategyHandler.get_stock_by_symbol('ADVANC')[0].get_stock_info()
        print(stock)

        self.strategyHandler.process_row(self.mock_market_row(price=30, volume=1000, flag='Sell'))
        self.strategyHandler.create_order_to_limit(symbol=self.symbol, side='Buy', volume=100, price=30)
        self.tradeSim.isMatch(self.mock_market_row(price=30, volume=1000, flag='Sell'))

        self.strategyHandler.process_row(self.mock_market_row(price=35, volume=1000, flag='Sell'))
        self.strategyHandler.create_order_to_limit(symbol=self.symbol, side='Buy', volume=100, price=35)
        self.tradeSim.isMatch(self.mock_market_row(price=35, volume=1000, flag='Sell'))

        # Simulate a sell that results in a max drawdown
        self.strategyHandler.process_row(self.mock_market_row(price=25, volume=1000, flag='Buy'))
        self.strategyHandler.create_order_to_limit(symbol=self.symbol, side='Sell', volume=100, price=25)
        self.tradeSim.isMatch(self.mock_market_row(price=25, volume=1000, flag='Buy'))

        # Check if max drawdown is calculated correctly
        max_dd = self.strategyHandler.get_max_draw_down()
        print(f"Max Drawdown: {max_dd}")
        self.assertTrue(max_dd < 0)

    def test_max_update_max_dd(self):
        self.tradeSim.update_market_prices({"AOT": 30.0, "PTT": 42.0})
        port_info = self.strategyHandler.get_portfolio_info()
        print(f"NAV before first buy: {port_info["Net Asset Value"]}")

        max_nav_after_second_buy = port_info["Max NAV"]
        min_nav_after_second_buy = port_info["Min NAV"]

        print(f"Max NAV recorded: {max_nav_after_second_buy}")
        print(f"Min NAV recorded: {min_nav_after_second_buy}")
        # Step 1: Buy at lower price (30, actual matched at 29.9)
        self.strategyHandler.process_row(self.mock_market_row(price=30, volume=100000, flag='Sell'))
        self.strategyHandler.create_order_to_limit(symbol=self.symbol, side='Buy', volume=10000, price=30)
        self.tradeSim.isMatch(self.mock_market_row(price=30, volume=100000, flag='Sell'))
        self.tradeSim.update_market_prices({"AOT": 30.0, "PTT": 42.0})

        port_info = self.strategyHandler.get_portfolio_info()
        print(f"NAV after first buy: {port_info["Net Asset Value"]}")

        max_nav_after_second_buy = port_info["Max NAV"]
        min_nav_after_second_buy = port_info["Min NAV"]

        print(f"Max NAV recorded: {max_nav_after_second_buy}")
        print(f"Min NAV recorded: {min_nav_after_second_buy}")

        self.strategyHandler.process_row(self.mock_market_row(price=35, volume=100000, flag='Sell'))
        self.strategyHandler.create_order_to_limit(symbol=self.symbol, side='Buy', volume=10000, price=35)
        self.tradeSim.isMatch(self.mock_market_row(price=35, volume=100000, flag='Sell'))


        self.tradeSim.update_market_prices({"AOT": 35.0, "PTT": 42.0})
        port_info = self.strategyHandler.get_portfolio_info()

        max_nav_after_second_buy = port_info["Max NAV"]
        min_nav_after_second_buy = port_info["Min NAV"]

        print(f"NAV after second buy: {port_info["Net Asset Value"]}")
        print(f"Max NAV recorded: {max_nav_after_second_buy}")
        print(f"Min NAV recorded: {min_nav_after_second_buy}")

        self.assertEqual(port_info["Net Asset Value"], max_nav_after_second_buy, msg="Max NAV should be updated to latest NAV")

        # Check max drawdown
        max_dd = self.strategyHandler.get_max_draw_down()
        print(f"Max Drawdown: {max_dd}")

        self.tradeSim.update_market_prices({"AOT": 25.0, "PTT": 42.0})
        port_info = self.strategyHandler.get_portfolio_info()

        max_nav_after_second_buy = port_info["Max NAV"]
        min_nav_after_second_buy = port_info["Min NAV"]

        print(f"NAV after second buy: {port_info["Net Asset Value"]}")
        print(f"Max NAV recorded: {max_nav_after_second_buy}")
        print(f"Min NAV recorded: {min_nav_after_second_buy}")


        self.tradeSim.update_market_prices({"AOT": 15.0, "PTT": 42.0})

        port_info = self.strategyHandler.get_portfolio_info()

        max_nav_after_second_buy = port_info["Max NAV"]
        min_nav_after_second_buy = port_info["Min NAV"]

        print(f"NAV after second buy: {port_info["Net Asset Value"]}")
        print(f"Max NAV recorded: {max_nav_after_second_buy}")
        print(f"Min NAV recorded: {min_nav_after_second_buy}")

        # Check max drawdown
        max_dd = self.strategyHandler.get_max_draw_down()
        print(f"Max Drawdown: {max_dd}")

        self.tradeSim.update_market_prices({"AOT": 40.0, "PTT": 42.0})

        port_info = self.strategyHandler.get_portfolio_info()

        max_nav_after_second_buy = port_info["Max NAV"]
        min_nav_after_second_buy = port_info["Min NAV"]

        print(f"NAV after second buy: {port_info["Net Asset Value"]}")
        print(f"Max NAV recorded: {max_nav_after_second_buy}")
        print(f"Min NAV recorded: {min_nav_after_second_buy}")

        # Check max drawdown
        max_dd = self.strategyHandler.get_max_draw_down()
        print(f"Max strategyHandler: {max_dd}")


        self.assertTrue(max_dd < 0, "Drawdown should be negative")

    def test_sell_stock_calculation(self):

        # Step 1: Buy at lower price (30, actual matched at 29.9)
        self.strategyHandler.process_row(self.mock_market_row(price=279, volume=100000, flag='Sell'))
        self.strategyHandler.create_order_to_limit(symbol=self.symbol, side='Buy', volume=10000, price=279)
        self.tradeSim.isMatch(self.mock_market_row(price=279, volume=100000, flag='Sell'))
        self.assertAlmostEqual(self.strategyHandler.get_cash_balance(),7195296.280, places=2)

        # Step 2: Sell again at higher price (35)
        self.strategyHandler.process_row(self.mock_market_row(price=282, volume=100000, flag='Buy'))
        self.strategyHandler.create_order_to_limit(symbol=self.symbol, side='Sell', volume=10000, price=282)
        self.tradeSim.isMatch(self.mock_market_row(price=282, volume=100000, flag='Buy'))

        self.tradeSim.update_market_prices({"AOT": 282.0, "PTT": 42.0})
        port_info = self.strategyHandler.get_portfolio_info()
        print(f"NAV after first buy: {port_info["Net Asset Value"]}")

        max_nav_after_second_buy = port_info["Max NAV"]
        min_nav_after_second_buy = port_info["Min NAV"]

        print(f"Max NAV recorded: {max_nav_after_second_buy}")
        print(f"Min NAV recorded: {min_nav_after_second_buy}")

        self.assertEqual(self.strategyHandler.get_cash_balance(),10000575.761)

    def test_win_and_sell_count(self):
        self.strategyHandler.process_row(self.mock_market_row(price=30, volume=100000, flag='Sell'))
        self.strategyHandler.create_order_to_limit(symbol=self.symbol, side='Buy', volume=100, price=30)
        self.tradeSim.isMatch(self.mock_market_row(price=30, volume=100000, flag='Sell'))

        self.strategyHandler.process_row(self.mock_market_row(price=35, volume=100000, flag='Sell'))
        self.strategyHandler.create_order_to_limit(symbol=self.symbol, side='Buy', volume=100, price=35)
        self.tradeSim.isMatch(self.mock_market_row(price=35, volume=100000, flag='Sell'))

        # Simulate a sell that results in a win
        self.strategyHandler.process_row(self.mock_market_row(price=45, volume=100000, flag='Buy'))
        self.strategyHandler.create_order_to_limit(symbol=self.symbol, side='Sell', volume=100, price=45)
        self.tradeSim.isMatch(self.mock_market_row(price=45, volume=100000, flag='Buy'))

        self.assertEqual(self.strategyHandler.get_number_of_wins(), 1)
        self.assertEqual(self.strategyHandler.get_number_of_sells(), 1)

    def test_roi_calculation(self):

        self.strategyHandler.process_row(self.mock_market_row(price=35, volume=100000, flag='Sell'))
        self.strategyHandler.create_order_to_limit(symbol=self.symbol, side='Buy', volume=100, price=35)
        self.tradeSim.isMatch(self.mock_market_row(price=35, volume=100000, flag='Sell'))
        self.tradeSim.update_market_prices({"AOT": 35.0, "PTT": 35.0})
        roi = self.strategyHandler.get_roi()
        print(f"ROI: {roi}")
        
        # Simulate a sell that results in a win
        self.strategyHandler.process_row(self.mock_market_row(price=45, volume=100000, flag='Buy'))
        self.strategyHandler.create_order_to_limit(symbol=self.symbol, side='Sell', volume=100, price=45)
        self.tradeSim.isMatch(self.mock_market_row(price=45, volume=100000, flag='Buy'))
        self.tradeSim.update_market_prices({"AOT": 45.0, "PTT": 45.0})
        roi = self.strategyHandler.get_roi()

        print(f"ROI: {roi}")



        self.assertTrue(roi > 0)



if __name__ == '__main__':
    unittest.main()