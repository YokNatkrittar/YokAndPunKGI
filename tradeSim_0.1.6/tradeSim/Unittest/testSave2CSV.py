import unittest
from tradeSim import Portfolio
from tradeSim import TradeSim
from tradeSim import Stock
import pandas as pd
import os
from datetime import datetime
import time

class TestSave2jsonMethod(unittest.TestCase):

    def setUp(self):
        self.tradeSim = TradeSim.tradeSim(team_name='JsonTeam')
        self.strategy_runner = self.tradeSim.get_strategy_runner()
        self.strategy_runner.create_order_to_limit(300, 30.0, "Buy", "AOT",10000,10000,self.mock_market_row(price=30, volume=300))
        self.tradeSim.isMatch(self.mock_market_row(price=30, volume=300))

    def mock_market_row(self, price, volume, timestamp=time.time()):
        return {
            'ShareCode': "AOT",
            'LastPrice': price,
            'Volume': volume,
            'TradeDateTime': pd.to_datetime(timestamp, unit='s')
        }
    def test_save_to_json(self):
        team_name = "JsonTeam"
        folder = "result"
        file_path = os.path.join(folder,team_name, f"{team_name}_portfolio.json")
        team_folder = os.path.join(folder, team_name)
        
        # Ensure the folder exists
        os.makedirs(folder, exist_ok=True)
        
        # Save the portfolio to JSON
        self.tradeSim.save_portfolio()
        
        # Check if the file was created
        self.assertTrue(os.path.exists(file_path))
        
        # Clean up
        os.remove(file_path)
        os.remove(os.path.join(folder, team_name, f"{team_name}_transaction_log.csv"))
        # time.sleep(1)  # Ensure file is removed before next test
        os.rmdir(team_folder)

    def test_load_from_file(self):
        folder = "result"
        team_name = "JsonTeam"
        file_path = os.path.join(folder, team_name, f"{team_name}_portfolio.json")
        team_folder = os.path.join(folder, team_name)

        os.makedirs(team_folder, exist_ok=True)
        self.tradeSim.save_portfolio()

        tradeSim = TradeSim.tradeSim(team_name)
        strategy_runner = tradeSim.get_strategy_runner()

        print(strategy_runner.get_all_stocks_info())
        
        self.assertEqual(len(strategy_runner.get_all_stocks_info()), 1)

        os.remove(file_path)
        os.remove(os.path.join(folder, team_name, f"{team_name}_transaction_log.csv"))
        os.rmdir(team_folder)

    def test_Port_info_in_json(self):
        folder = "result"
        team_name = "JsonTeam"
        file_path = os.path.join(folder, team_name, f"{team_name}_portfolio.json")
        team_folder = os.path.join(folder, team_name)

        os.makedirs(team_folder, exist_ok=True)
        self.tradeSim.save_portfolio()

        tradeSim = TradeSim.tradeSim(team_name)
        strategy_runner = tradeSim.get_strategy_runner()

        print(strategy_runner.get_portfolio_info())
        
        self.assertEqual(len(strategy_runner.get_all_stocks_info()), 1)

        os.remove(file_path)
        os.remove(os.path.join(folder, team_name, f"{team_name}_transaction_log.csv"))
        os.rmdir(team_folder)

    def test_stock_in_port(self):
        team_name = "JsonTeam"
        folder = "result"
        file_path = os.path.join(folder,team_name, f"{team_name}_portfolio.json")
        team_folder = os.path.join(folder, team_name)
        
        # Ensure the folder exists
        os.makedirs(team_folder, exist_ok=True)

        # update market prices
        self.tradeSim.update_market_prices({"AOT": 28.9, "PTT": 42.0})
        
        # Save the portfolio to JSON
        self.tradeSim.save_portfolio()

        print(self.strategy_runner.get_all_stocks_info())

        # Check if a specific stock info is in the portfolio
        stocks_info = self.strategy_runner.get_all_stocks_info()
        self.assertIn("AOT", [stock["Symbol"] for stock in stocks_info])

        Aot = self.strategy_runner.get_stock_by_symbol("AOT")

        # print(f"AOT Stock Info: {Aot[0].get_stock_info()}")

        self.assertEqual(Aot[0].get_stock_info()["Symbol"], "AOT")
        self.assertEqual(Aot[0].get_stock_info()["Actual Volume"], 300)
        self.assertEqual(Aot[0].get_stock_info()["Buy Price"], 30.3)
        self.assertEqual(Aot[0].get_stock_info()["Market Price"], 28.9)
        self.assertEqual(Aot[0].get_stock_info()["Amount Cost"], 9090.25)

        
        # Clean up
        os.remove(file_path)
        os.remove(os.path.join(folder, team_name, f"{team_name}_transaction_log.csv"))
        os.rmdir(team_folder)

    