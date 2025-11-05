from collections import defaultdict
import csv
import json
from . import Stock
import os
from datetime import datetime
import inspect


class portfolio:
    def __init__(
        self,
        owner,
        stocksList=None,
        amountByCost=0.0,
        unrealized=0.0,
        unrealizedInPercentage=0.0,
        realized=0.0,
        cashbalance=10000000.0,
        cashbalance_start=None,
        prevousDay_maxDD=None,
        nav=0.0,
        max_nav=None,
        min_nav=None,
        max_Draw_down=0.0,
        No_win=0,
        No_sell=0,
    ):
        self.owner = owner
        self.stocksList = stocksList if stocksList is not None else []
        self.amountByCost = amountByCost
        self.unrealized = unrealized
        self.unrealizedInPercentage = unrealizedInPercentage
        self.realized = realized
        self.cashbalance = cashbalance
        self.initial_cash = 10000000.0
        self.prevousDay_maxDD = prevousDay_maxDD
        self.cashbalance_start = cashbalance_start if cashbalance_start is not None else 10000000.0
        self.nav = nav
        self.max_nav = max_nav
        self.min_nav = min_nav
        self.max_Draw_down = max_Draw_down
        self.No_win = No_win
        self.No_sell = No_sell

    def add_stock(self, stock):
        # check if add stock is call for create_order
        caller = inspect.stack()[1].function
        if caller != "_process_buy_order" and caller != "_process_market_order":
            print(caller)
            raise ValueError(f"add stock must be called from create_order(). unable to add stock from {caller}()")

        self.stocksList.append(stock)
        self.update_portfolio_totals()
        self.update_avg_stocks_by_symbol(stock.get_symbol())

    def decrease_stock_volume(self, symbol, volume, price):

        self.stocksList.sort(key=lambda stock: stock.buy_time)

        remaining_volume = volume
        total_realized = 0.0
        if self._isWin((price * volume), self._cal_avg_cost(symbol) * volume):
            self._increase_numberOfWin()
        for s in list(self.stocksList):

            if remaining_volume == 0:
                break

            if s.get_symbol() == symbol:

                if s.get_realized() != 0.0:
                    total_realized = s.get_realized()

                vol_to_decrease = min(s.get_actual_vol(), remaining_volume)

                # Calculate realized profit/loss
                realized_profit = (price * vol_to_decrease) - (
                    s.get_buy_price() * vol_to_decrease
                )
                total_realized += realized_profit
                self.realized += realized_profit

                s.add_realized(total_realized)

                # count number of sell count
                self._increase_numberOfSell()

                # decrease volume of stock
                s.decreaseStockVolume(vol_to_decrease)
                remaining_volume -= vol_to_decrease

                # If actual_vol becomes 0 or below, remove this stock
                if s.get_actual_vol() <= 0:
                    self.stocksList.remove(s)

        self.update_portfolio_totals()
        self.update_avg_stocks_by_symbol(symbol)

    def update_avg_stocks_by_symbol(self, symbol):
            for stocks in self.get_stock_by_symbol(symbol):
                new_price = stocks.get_mkt_price()
                symbol_avg_cost = self._cal_avg_cost(symbol)
                stocks.updateStockMk_value(new_price, symbol_avg_cost)

    def update_sold_stock_valueToPort(self, amount):
        self.cashbalance += amount

    def update_Buy_stock_valueToPort(self, amount):
        self.cashbalance -= amount

    def _update_max_min_nav(self):
        nav = self.get_nav()

        if self.max_nav is None or nav > self.max_nav:
            self.max_nav = nav
            self.min_nav = nav
        elif nav < self.min_nav:
            self.min_nav = nav

    def _calUnrealized(self):
        self.unrealized = self.market_value - self.amount_cost

    def _calUnrealizedInPercentagee(self):
        self.unrealizedInPercentage = (
            (self.unrealized / self.amount_cost) * 100 if self.amount_cost != 0 else 0.0
        )

    def _cal_avg_cost(self, symbol):
        symbol_stocks = self.get_stock_by_symbol(symbol)
        total_volume = 0
        total_cost = 0.0
        for stock in symbol_stocks:
            volume = stock.get_actual_vol()
            price = stock.get_buy_price()
            total_volume += volume
            total_cost += price * volume

        if total_volume == 0:
            return 0.0

        avg_cost = total_cost / total_volume
        return avg_cost

    def _cal_maxDD(self):
        if self.max_nav and self.min_nav and self.max_nav != 0:
            current_dd = ((self.min_nav - self.max_nav) / self.max_nav) * 100
            self.prevousDay_maxDD = min(self.prevousDay_maxDD or 0, current_dd)
            self.max_Draw_down = self.prevousDay_maxDD

    def _cal_winRate(self):
        if self.No_sell == 0 or self.No_win == 0:
            return 0
        return (self.No_win / self.No_sell) * 100

    def _calculate_nav(self):
        self.nav = self.get_unrealized() + self.cashbalance + self.get_amount_by_cost()

    def calculate_roi(self):
        return (
            ((self.get_nav() - self.initial_cash) / self.initial_cash * 100) 
        )

    def _cal_relativeDrawdown(self):
        return (self.max_Draw_down / self.initial_cash) / 100

    def update_portfolio_totals(self):
        total_amount = 0.0
        total_unrealized = 0.0
        total_realized = 0.0

        for stock in self.stocksList:
            total_amount += stock.get_amount_cost()
            total_unrealized += stock.get_unrealized()
            total_realized += stock.get_realized()
            


        self.amountByCost = total_amount
        self.unrealized = total_unrealized
        self.unrealizedInPercentage = (
            (self.unrealized / self.amountByCost) * 100
            if self.amountByCost != 0
            else 0.0
        )
        self._calculate_nav()
        self._update_max_min_nav()
        self._cal_maxDD()

    def _cal_calmar_ratio(self):
        if self.max_Draw_down == 0:
            return 0
        return self.calculate_roi() / self.max_Draw_down

    def update_market_prices(self, price_updates: dict):
        """
        price_updates: dict mapping symbol (str) -> new market price (float)
        """
        for stock in self.stocksList:
            if stock.get_symbol() in price_updates:
                new_price = price_updates[stock.get_symbol()]
                symbol_avg_cost = self._cal_avg_cost(stock.get_symbol())
                stock.updateStockMk_value(new_price, symbol_avg_cost)
        self.update_portfolio_totals()

    def has_stock(self, symbol, volume):
        total_volume = 0.0
        for stock in self.stocksList:
            if stock.get_symbol() == symbol:
                total_volume += stock.get_actual_vol()
        if total_volume >= volume:
            return True
        return False

    def cal_realized(self, total_cost, total_value):
        return total_value - total_cost

    # getter methods
    def get_owner(self):
        return self.owner

    def get_stocks_list(self):
        return self.stocksList

    def get_amount_by_cost(self):
        return self.amountByCost

    def get_unrealized(self):
        return self.unrealized

    def get_unrealized_in_percentage(self):
        return self.unrealizedInPercentage

    def get_realized(self):
        return self.realized

    def get_cash_balance(self):
        return self.cashbalance

    def get_initial_cash(self):
        return self.initial_cash

    def get_prevous_day_max_dd(self):
        return self.prevousDay_maxDD

    def get_nav(self):
        return self.nav

    def get_max_nav(self):
        return self.max_nav

    def get_min_nav(self):
        return self.min_nav

    def get_max_draw_down(self):
        return self.max_Draw_down

    def get_number_of_wins(self):
        return self.No_win

    def get_number_of_sells(self):
        return self.No_sell

    def get_all_stocks_info(self):
        """
        Returns a list of aggregated stock info dictionaries by symbol.
        Combines multiple lots of the same stock into a single summary row.
        """
        aggregated = defaultdict(
            lambda: {
                "Symbol": "",
                "Buy Price": 0.0,
                "Actual Volume": 0,
                "Total Cost": 0.0,
                "Market Value": 0.0,
                "Unrealized P&L": 0.0,
                "Realized P&L": 0.0,
                "Buy time": "",
                "Market Price": 0.0,
            }
        )

        for stock in self.stocksList:
            info = stock.get_stock_info()
            symbol = info["Symbol"]

            aggregated[symbol]["Symbol"] = symbol
            aggregated[symbol]["Buy Price"] = info["Buy Price"]
            aggregated[symbol]["Actual Volume"] += info["Actual Volume"]
            aggregated[symbol]["Total Cost"] += info["Amount Cost"]
            aggregated[symbol]["Market Value"] += info["Market Value"]
            aggregated[symbol]["Unrealized P&L"] += info["Unrealized P&L"]
            aggregated[symbol]["Realized P&L"] += info["Realized P&L"]
            aggregated[symbol]["Buy time"] = info["Buy time"]
            aggregated[symbol]["Market Price"] = info["Market Price"]

        result = []
        for sym_data in aggregated.values():
            actual_vol = sym_data["Actual Volume"]
            avg_cost = sym_data["Total Cost"] / actual_vol if actual_vol != 0 else 0.0
            unrealized_pct = (
                (sym_data["Unrealized P&L"] / sym_data["Total Cost"] * 100)
                if sym_data["Total Cost"] != 0
                else 0.0
            )

            result.append(
                {
                    "Symbol": sym_data["Symbol"],
                    "Buy Price": sym_data["Buy Price"],
                    "Actual Volume": actual_vol,
                    "Average Cost": avg_cost,
                    "Market Price": sym_data["Market Price"],
                    "Amount Cost": sym_data["Total Cost"],
                    "Market Value": sym_data["Market Value"],
                    "Unrealized P&L": sym_data["Unrealized P&L"],
                    "Unrealized %": unrealized_pct,
                    "Realized P&L": sym_data["Realized P&L"],
                    "Buy time": sym_data["Buy time"],
                }
            )

        return result

    def get_stock_by_symbol(self, symbol):
        return [stock for stock in self.stocksList if stock.get_symbol() == symbol]

    def get_total_stock_volume_by_symbol(self, symbol):
        total_volume = 0
        all_stocks_of_symbol = self.get_stock_by_symbol(symbol)
        for stock in all_stocks_of_symbol:
            total_volume += stock.get_actual_vol()
        return total_volume

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

        return {
            "Owner": self.owner,
            "Number of Stocks": len(self.stocksList),
            "Total Cost": round(self.amountByCost, 2),
            "Unrealized P&L": round(self.unrealized, 2),
            "Unrealized %": round(self.unrealizedInPercentage, 2),
            "Realized P&L": round(self.realized, 2),
            "Cash Balance": round(self.cashbalance, 2),
            "Net Asset Value": round(self.nav, 2),
            "Max NAV": round(self.max_nav, 2) if self.max_nav is not None else None,
            "Min NAV": round(self.min_nav, 2) if self.min_nav is not None else None,
            "Max Drawdown (%)": (
                round(self.max_Draw_down, 2) if self.max_Draw_down is not None else None
            ),
            "Relative Drawdown": self._cal_relativeDrawdown(),
            "Calmar Ratio": self._cal_calmar_ratio(),
            "Previous Day Max DD (%)": (
                round(self.prevousDay_maxDD, 2)
                if self.prevousDay_maxDD is not None
                else None
            ),
            "Number of Wins": self.No_win,
            "Number of Sells": self.No_sell,
            "Win Rate": self._cal_winRate(),
            "Return rate": self.calculate_roi(),
        }

    def get_All_stock_count_by_symbol(self):
        """
        Returns a dict mapping symbol -> number of buy entries in stocksList.
        Each entry counts as one buy regardless of volume.
        """
        buy_count = defaultdict(int)
        for stock in self.stocksList:
            symbol = stock.get_symbol()
            buy_count[symbol] += 1
        return dict(buy_count)

    def _increase_numberOfWin(self):
        self.No_win += 1

    def _increase_numberOfSell(self):
        self.No_sell += 1

    def _isWin(self, price, avg_cost):
        # print(f"Checking if price {price} is greater than avg_cost {avg_cost}")
        return price > avg_cost

    def export_stocks_to_csv(self):
        stocks = self.get_all_stocks_info()
        if not stocks:
            print("No stock in portfolio")
            return

        keys = ["Symbol", "Actual Volume", "Buy Price", "Buy time"]

    def save_to_file(self, owner):

        filename = owner + "_" + "portfolio.json"
        folder_path = os.path.join("result", self.owner)
        os.makedirs(folder_path, exist_ok=True)

        filename = os.path.join(folder_path, filename)

        data = {
            "owner": self.owner,
            "cashbalance_start": self.cashbalance_start,
            "cashbalance": self.cashbalance,
            "realized": self.realized,
            "stocksList": [stock.to_dict() for stock in self.stocksList],
            "No_win": self.No_win,
            "No_sell": self.No_sell,
            "prevousDay_maxDD": self.prevousDay_maxDD,
        }
        with open(filename, "w") as f:
            json.dump(data, f, indent=4, default=str)

    def save_summary_csv(self,daily_ticks_timestamp):
        # Define folder and filename
        folder_path = os.path.join("result", self.owner)
        os.makedirs(folder_path, exist_ok=True)
        summary_file = os.path.join(folder_path, f"{self.owner}_portfolio_summary.csv")

        # Calculate derived stats
        num_stocks = len(self.stocksList)
        total_cost = sum(stock.amount_cost for stock in self.stocksList)
        unrealized = sum(stock.unrealized for stock in self.stocksList)
        unrealized_percent = (unrealized / total_cost * 100) if total_cost else 0
        nav = self.get_nav()
        max_nav = self.max_nav
        min_nav = self.min_nav
        max_dd = self.max_Draw_down  # in %
        relative_dd = (max_dd / 100) if max_nav else 0
        calmar = ((nav - 10000000) / 10000000) / abs(max_dd / 100) if max_dd != 0 else 0
        win_rate = (self.No_win / self.No_sell * 100) if self.No_sell else 0
        return_rate = ((nav - 10000000) / 10000000 * 100)  # assuming 10M initial

        # Prepare row
        row = [
            self.owner,
            num_stocks,
            round(total_cost, 2),
            round(unrealized, 2),
            round(unrealized_percent, 1),
            round(self.realized, 2),
            round(self.cashbalance_start, 2),
            round(self.cashbalance, 2),
            round(nav, 2),
            round(max_nav, 2),
            round(min_nav, 2),
            round(max_dd, 2),
            relative_dd,
            calmar,
            round(self.prevousDay_maxDD, 2),
            self.No_win,
            self.No_sell,
            round(win_rate, 1),
            round(return_rate, 10),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            daily_ticks_timestamp.strftime("%Y-%m-%d %H:%M:%S")
        ]

        # Write header and row
        header = [
            "Owner", "Number of Stocks", "Total Cost", "Unrealized P&L", "Unrealized %",
            "Realized P&L", "cashbalance start", "Cash Balance", "Net Asset Value", "Max NAV", "Min NAV",
            "Max Drawdown (%)", "Relative Drawdown", "Calmar Ratio",
            "Previous Day Max DD (%)", "Number of Wins", "Number of Sells",
            "Win Rate", "Return rate", "Saved At", "Daily Ticks Time"
        ]

        write_header = not os.path.exists(summary_file)

        with open(summary_file, mode='a', newline='') as f:
            writer = csv.writer(f)
            if write_header:
                writer.writerow(header)
            writer.writerow(row)

        

    @classmethod
    def load_from_file(cls, owner):

        file_path = os.path.join("result", owner, owner + "_" + "portfolio.json")

        if not os.path.exists(file_path):
            raise FileNotFoundError(
                f"Portfolio file for {owner} does not exist: {file_path}"
            )

        with open(file_path, "r") as f:
            data = json.load(f)
            stocks_data = data["stocksList"]
            stocksList = [Stock.stock.from_dict(d) for d in stocks_data]
        return cls(
            owner=data["owner"],
            stocksList=stocksList,
            cashbalance=data["cashbalance"],
            cashbalance_start=data["cashbalance"],
            realized=data["realized"],
            No_win=data.get("No_win", 0),
            No_sell=data.get("No_sell", 0),
            prevousDay_maxDD=data.get("prevousDay_maxDD", None),
        )
