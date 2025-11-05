from . import Order
from datetime import timedelta

class strategy_runner:
    def __init__(self, tradeSim):
        """
        Initialize the strategy runner for executing strategies in the trade simulation.
        """
        self.tradeSim = tradeSim

    def create_order_to_limit(self, volume, price, side, symbol, cum_sell_volume, cum_buy_volume, mkt_data):
        return self.tradeSim.create_order_to_limit(volume, price, side, symbol, cum_sell_volume, cum_buy_volume, mkt_data)
    
    def create_order_at_market(self, volume, side, symbol, cum_sell_volume, cum_buy_volume, mkt_data):
        return self.tradeSim.create_order_at_market(volume, side, symbol, cum_sell_volume, cum_buy_volume, mkt_data)
    
    def check_port_has_stock(self, symbol, volume):
        """
        Check if the portfolio has a specific stock with the given volume.
        """
        return self.tradeSim.portfolio.has_stock(symbol, volume)

    def get_owner(self):
        """
        Get the owner of the portfolio. 
        """
        return self.tradeSim.portfolio.get_owner()
    
    def get_all_stocks_info(self):
        """
        Returns a list of summarized stock information grouped by symbol.

        This method aggregates multiple lots of the same stock into a single summary entry.
        It computes the total volume, total cost, average cost, market value, and both realized and unrealized P&L
        for each unique stock symbol in the portfolio.

        Returns
        -------
        list of dict
            A list where each dictionary contains:
                - "Symbol": str, stock symbol.
                - "Buy Price": float, original buy price of the first lot (not averaged).
                - "Actual Volume": int, total remaining volume held for the symbol.
                - "Average Cost": float, total cost divided by total volume.
                - "Market Price": float, current market price.
                - "Amount Cost": float, total cost for the symbol.
                - "Market Value": float, current market value.
                - "Unrealized P&L": float, total unrealized profit/loss.
                - "Unrealized %": float, percentage of unrealized gain/loss.
                - "Realized P&L": float, total realized profit/loss from sells.
                - "Buy time": str, timestamp of the first buy (not aggregated across lots).
        """
        return self.tradeSim.portfolio.get_all_stocks_info()
    
    def get_portfolio_info(self):
        """
        Returns a summary of the portfolio's current state.

        The summary includes performance metrics, NAV statistics, trading results,
        and both realized and unrealized profit/loss information.

        Returns
        -------
        dict
            A dictionary containing:
                - "Owner": str, portfolio owner name.
                - "Number of Stocks": int, number of stock entries in the portfolio.
                - "Total Cost": float, total cost spent on current holdings.
                - "Unrealized P&L": float, unrealized profit or loss.
                - "Unrealized %": float, percentage of unrealized gain/loss.
                - "Realized P&L": float, realized profit or loss.
                - "Cash Balance": float, remaining cash.
                - "Net Asset Value": float, current NAV (cash + market value of holdings).
                - "Max NAV": float or None, highest NAV observed.
                - "Min NAV": float or None, lowest NAV observed.
                - "Max Drawdown (%)": float or None, max drawdown as a percentage.
                - "Relative Drawdown": float or None, current drawdown relative to NAV.
                - "Calmar Ratio": float or None, ratio of return to max drawdown.
                - "Previous Day Max DD (%)": float or None, prior day's max drawdown.
                - "Number of Wins": int, total number of profitable trades.
                - "Number of Sells": int, total number of sell trades executed.
                - "Win Rate": float, win rate across all sell trades.
                - "Return rate": float, overall portfolio ROI.
        """
        return self.tradeSim.portfolio.get_portfolio_info()
    
    def get_stock_by_symbol(self,symbol):
        """
        Get a specific stock by its symbol from the portfolio.
        """
        return self.tradeSim.portfolio.get_stock_by_symbol(symbol)
    
    def get_total_stock_volume_by_symbol(self, symbol):
        """
        Get the total volume of a specific stock symbol in the portfolio.
        """
        return self.tradeSim.portfolio.get_total_stock_volume_by_symbol(symbol)
    
    def get_cash_balance(self):
        """
        Get the current cash balance in the portfolio.
        """
        return self.tradeSim.portfolio.get_cash_balance()
    
    def get_roi(self):
        """
        Calculate the return on investment (ROI) for the portfolio.
        """
        return self.tradeSim.portfolio.calculate_roi()
    
    def get_max_draw_down(self):
        """
        Get the maximum drawdown of the portfolio.
        This is the largest observed loss from a peak to a trough of a portfolio, before a new peak is attained.
        """
        return self.tradeSim.portfolio.get_max_draw_down()
    
    def get_number_of_wins(self):
        """
        Get the total number of winning trades in the portfolio.
        A winning trade is defined as a sell transaction that results in a profit.
        """
        return self.tradeSim.portfolio.get_number_of_wins()
    
    def get_number_of_sells(self):
        """
        Get the total number of sell transactions executed in the portfolio.
        """
        return self.tradeSim.portfolio.get_number_of_sells()