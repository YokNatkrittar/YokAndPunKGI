from . import Portfolio
from . import Execution
from . import Strategy_runner
from . import Order
from datetime import timedelta
import os
import threading
lock = threading.Lock()

import os
from datetime import datetime

logged_errors = set()

class tradeSim:
    def __init__(self, team_name, load_existing=True, folder="result", ):
        self.error_logger = ErrorLogger(team_name)
        """
        Initialize the trade simulation environment for a simulation.
        ----------
        Parameter
        team_name: Name of the team.
        """
        # create directory if it does not exist
        team_folder = os.path.join(folder, team_name)
        os.makedirs(team_folder, exist_ok=True) 

        portfolio_file_name = f"{team_name}_portfolio.json"
        file_path = os.path.join(folder,team_name, portfolio_file_name)

        if load_existing and os.path.exists(file_path):
            self.portfolio = Portfolio.portfolio.load_from_file(team_name)
            print(f"[INFO] Loaded existing portfolio from '{file_path}'")
        else:
            self.portfolio = Portfolio.portfolio(team_name)
            print(f"[INFO] Created new portfolio for '{team_name}'")
            self.portfolio.save_to_file(team_name)
        self.execution = Execution.execution(team_name)

    def create_order_to_limit(self, volume, price, side, symbol, cum_sell_volume, cum_buy_volume, mkt_data):
        with lock:
            limit_order = None
            try:
                limit_order = Order.order(
                    ownerPortfolio=self.portfolio,
                    volume=volume,
                    price=price,
                    side=side,
                    symbol=symbol,
                    cum_sell_volume=cum_sell_volume,
                    cum_buy_volume=cum_buy_volume,
                    timestamp= (mkt_data['TradeDateTime'] - timedelta(hours=7)).timestamp()
                )
                self.execution.addOrderToOrders_Book(limit_order, mkt_data)

            except ValueError as e:
                self.error_logger.log_error(e)
                return e
            except FileNotFoundError as e:
                self.error_logger.log_error(e)
                return e
            except KeyError as e:
                self.error_logger.log_error(e)
                return e

            return "Order for {symbol} (Vol: {volume}, Price: {price}, Side: {side}) created successfully.".format(
                symbol=symbol,
                volume=volume,
                price=price,
                side=side
            )

    def create_order_at_market(self, volume, side, symbol, cum_sell_volume, cum_buy_volume, mkt_data):
        with lock:
            new_order = None
            try:
                new_order = Order.order(
                    ownerPortfolio=self.portfolio,
                    volume=volume,
                    price=mkt_data['LastPrice'],
                    side=side,
                    symbol=symbol,
                    cum_sell_volume=cum_sell_volume,
                    cum_buy_volume=cum_buy_volume,
                    timestamp= (mkt_data['TradeDateTime'] - timedelta(hours=7)).timestamp()
                )
                self.execution.isMatchMarketOrder(mkt_data,new_order)

            except ValueError as e:
                self.error_logger.log_error(e)
                return e
            except FileNotFoundError as e:
                self.error_logger.log_error(e)
                return e
            except KeyError as e:
                self.error_logger.log_error(e)
                return e

            return "Order for {symbol} (Vol: {volume}, Price: {price}, Side: {side}) created successfully.".format(
                symbol=symbol,
                volume=volume,
                price=mkt_data['LastPrice'],
                side=side
            )

    def get_strategy_runner(self):
        """
        Returns the strategy runner instance for executing strategies.
        """
        return Strategy_runner.strategy_runner(self)
    
    def save_portfolio(self):
        """ 
        Save the current portfolio state to  JSONfile. 
        """
        self.portfolio.save_to_file(self.portfolio.get_owner())
    
    def save_summary_csv(self, trading_date):
        self.portfolio.save_summary_csv(trading_date)

    def create_transaction_summarize(self, team_name):
        """
        Create a transaction summary for the team.
        """
        self.execution.PortSummarize.create_transaction_summarize(team_name)

    def isOrderbooksEmpty(self):
        """
        Check if the order book is empty.
        """
        return len(self.execution.Orders_Book) == 0
    
    def isMatch(self, row):
        with lock:
            return self.execution.isMatch(row)
    
        # update market prices in portfolio
    def update_market_prices(self, price_update):
        """
        Update the market prices in the portfolio based on the provided price update.
        """
        self.portfolio.update_market_prices(price_update)
        
    def flushTransactionLog(self):
        self.execution.flushTransactionLog()

    def flushErrorLogger(self):
        self.error_logger.flush_logs()


class ErrorLogger:
    def __init__(self, team_name, filename_suffix="error_log.txt"):
        self.error_log = []
        self.team_name = team_name

        folder = os.path.join("result", team_name)
        os.makedirs(folder, exist_ok=True)
        self.txt_file = os.path.join(folder, f"{team_name}_{filename_suffix}")

        # Write header once
        if not os.path.exists(self.txt_file):
            with open(self.txt_file, "w", encoding="utf-8") as f:
                f.write("Timestamp | Error Message\n")
                f.write("-" * 80 + "\n")

    def log_error(self, error: Exception):
        err_msg = str(error)
        # Avoid duplicates within current runtime
        if err_msg not in [e["message"] for e in self.error_log]:
            self.error_log.append({
                "timestamp": datetime.now(),
                "message": err_msg
            })

    def flush_logs(self):
        if not self.error_log:
            return

        with open(self.txt_file, "a", encoding="utf-8") as f:
            for e in self.error_log:
                f.write(f"{e['timestamp']} | {e['message']}\n")

        self.error_log.clear()
