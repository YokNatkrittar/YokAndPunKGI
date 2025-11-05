from . import Stock
from . import TransactionLog
from . import PortSummarize as ps
from . import CommissionService
import pandas as pd
import os
import bisect
import logging


class execution:
    PortSummarize = ps.summarize

    def __init__(
        self,
        team_name,
        orders_book=None,
    ):
        self.Orders_Book = orders_book if orders_book is not None else []
        self.tranLog = TransactionLog.Transaction(team_name)

    def addOrderToOrders_Book(self, new_order, row):
        if new_order is None:
            return "Cannot add an invalid/None order."
        if new_order.get_side() == "Buy":
            self.Orders_Book.append(new_order)
            return f"Order {new_order.get_order_number()} added to book ({new_order.get_symbol()})."
        elif new_order.get_side() == "Sell":
            self.Orders_Book.append(new_order)
            return f"Order {new_order.get_order_number()} added to book ({new_order.get_symbol()})."

    def isMatch(self, row):

        if len(self.Orders_Book) == 0:
            return "No order in Order book"

        for order in self.Orders_Book:

            if self._is_order_valid(row, order):
                if order.get_side() == "Buy":
                    self._process_buy_order(order)
                if order.get_side() == "Sell":
                    self._process_sell_order(order)
            else:
                self.removeOrder(order)
                return f"Order does not match with valid for matching order in market."
    def isMatchMarketOrder(self, row, market_order):    
        if market_order is not None:
            if self._is_order_valid(row, market_order):
                self._process_market_order(market_order)
            else:
                return f"Limit order {market_order.get_order_number()} does not match with valid for matching order in market."

    def _is_order_valid(self, row, order):
        order_time = pd.to_datetime(order.get_timestamp(), unit="s")

        if row["ShareCode"] != order.get_symbol():
            return False

        if row["TradeDateTime"] < order_time:
            return False

        if order.get_side() == "Buy" and row["LastPrice"] > (CommissionService.commissionService._get_slippage(order.get_price()) + order.get_price()):
            return False  # Order has lower price than market price
        if order.get_side() == "Sell" and row["LastPrice"] < (CommissionService.commissionService._get_slippage(order.get_price()) - order.get_price()):
            return False  # order has higher price than market price
        return True

    def _process_buy_order(self, order):
        Buy_value = CommissionService.commissionService.cal_commissionAndVat(
            order.get_volume(), order.get_price(), order.get_side()
        )
        new_stock = Stock.stock(
            order.get_symbol(),
            order.get_volume(),
            Buy_value,
            order.get_price(),
            order.get_timestamp(),
        )
        order.get_ownerPortfolio().add_stock(new_stock)
        order.get_ownerPortfolio().update_Buy_stock_valueToPort(
            Buy_value * order.get_volume()
        )
        self.tranLog.create_transaction_log(order)

        self.removeOrder(order)

    def _process_sell_order(self, order):
        Sell_value = CommissionService.commissionService.cal_commissionAndVat(
            order.get_volume(), order.get_price(), order.get_side()
        )
        order.get_ownerPortfolio().decrease_stock_volume(
            order.get_symbol(), order.get_volume(), Sell_value
        )
        order.get_ownerPortfolio().update_sold_stock_valueToPort(
            Sell_value * order.get_volume()
        )
        self.tranLog.create_transaction_log(order)
        self.removeOrder(order)

    def _process_market_order(self, order):
        if order.get_side() == "Buy":
            Buy_value = CommissionService.commissionService.cal_commissionAndVat(
            order.get_volume(), order.get_price(), order.get_side()
            )
            new_stock = Stock.stock(
                order.get_symbol(),
                order.get_volume(),
                Buy_value,
                order.get_price(),
                order.get_timestamp(),
            )
            print(f"Adding stock {new_stock.get_symbol()} with volume {new_stock.get_actual_vol()} at price {new_stock.get_buy_price()}")
            order.get_ownerPortfolio().add_stock(new_stock)
            order.get_ownerPortfolio().update_Buy_stock_valueToPort(
                Buy_value * order.get_volume()
            )
            self.tranLog.create_transaction_log(order)
        elif order.get_side() == "Sell":
            Sell_value = CommissionService.commissionService.cal_commissionAndVat(
            order.get_volume(), order.get_price(), order.get_side()
            )
            order.get_ownerPortfolio().decrease_stock_volume(
                order.get_symbol(), order.get_volume(), Sell_value
            )
            order.get_ownerPortfolio().update_sold_stock_valueToPort(
                Sell_value * order.get_volume()
            )
            self.tranLog.create_transaction_log(order)

    def removeOrder(self, order):
        self.Orders_Book.remove(order)

    def getOrderbooksSize(self):
        return len(self.Orders_Book)

    def isOrderbooksEmpty(self):
        return self.getOrderbooksSize() == 0

    def flushTransactionLog(self):
        self.tranLog.flush_logs()