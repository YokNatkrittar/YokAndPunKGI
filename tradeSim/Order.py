import time
import csv
import os
import bisect
from . import CommissionService


class order:
    _order_counter = 1
    _set50_symbols = set()
    _csv_loaded = False

    @classmethod
    def load_set50_symbols(cls, csv_path=None):
        if cls._csv_loaded:
            return

        if csv_path is None:
            base_dir = os.path.dirname((__file__))
            csv_path = os.path.join(
                base_dir, "..", "marketInfo", "symbolSET50", "Symbol_SET50.csv"
            )
            csv_path = os.path.abspath(csv_path)

        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"[ERROR] Cannot find SET50 list at '{csv_path}'")

        with open(csv_path, mode="r", newline="", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            headers = [h.strip() for h in reader.fieldnames]

            symbol_col = None
            for h in headers:
                if h.lower() == "symbol":
                    symbol_col = h
                    break
            if symbol_col is None:
                raise KeyError("[ERROR] 'Symbol' column not found in CSV headers.")

            for row in reader:
                symbol = row[symbol_col].strip().upper()
                cls._set50_symbols.add(symbol)

        cls._csv_loaded = True

    def __init__(
        self,
        ownerPortfolio,
        volume,
        price,
        side,  # 'Buy' or 'Sell'
        symbol,
        cum_sell_volume,
        cum_buy_volume,
        timestamp=None,
    ):
        order.load_set50_symbols()
        is_valid, reason = self.validate_order(
            volume, side, symbol, ownerPortfolio, price, cum_sell_volume, cum_buy_volume
        )
        if not is_valid:
            raise ValueError(
                f"[ERROR] Order for {symbol} (Vol: {volume}, Price: {price}, Side: {side}) skipped due to {reason}"
            )
        self.order_number = f"ORD{order._order_counter:05d}"
        order._order_counter += 1

        self.ownerPortfolio = ownerPortfolio
        self.volume = volume
        self.price = price
        self.side = side
        self.symbol = symbol
        self.cum_sell_volume = cum_sell_volume
        self.cum_buy_volume = cum_buy_volume
        self.timestamp = timestamp if timestamp is not None else time.time()


    def validate_order(self, volume, side, symbol, ownerPortfolio, price, cum_sell_volume, cum_buy_volume):
        cashBalance = ownerPortfolio.get_cash_balance()
        
        if (volume % 100.0) != 0 and volume > 0:
            return False, "Volume must be a multiple of 100.SS S"
        
        if side.capitalize() not in {"Buy", "Sell"}:
            return False, f"Invalid side '{side}'. Must be 'Buy' or 'Sell'. Case sensitive."
        
        if symbol.upper() not in self._set50_symbols:
            return False, f"Symbol '{symbol}' is not in SET50."
        
        if (
            CommissionService.commissionService.verify_transaction(
                volume=volume, price=price, cashBalance=cashBalance
            )
            is False
            and side == "Buy"
        ):
            return False, "Insufficient cash balance to cover transaction costs."
        
        if ownerPortfolio.has_stock(symbol, volume) is False and side == "Sell":
            return (
                False,
                f"Cannot sell {symbol} as it is not in the portfolio or insufficient volume.",
            )
            
        if side == "Buy" and volume > cum_sell_volume:
            return False, "Order's buy volume exceeds the cumulative sell volume from the daily ticks."
        
        if side == "Sell" and volume > cum_buy_volume:
            return False, "Order's sell volume exceeds the cumulative buy volume from the daily ticks."
        
        return True, ""
        
        

    # --------- Getter Methods ---------
    def get_order_number(self):
        return self.order_number

    def get_ownerPortfolio(self):
        return self.ownerPortfolio

    def get_volume(self):
        return self.volume

    def get_price(self):
        return self.price

    def get_side(self):
        return self.side

    def get_symbol(self):
        return self.symbol

    def get_timestamp(self):
        return self.timestamp

    def get_formatted_timestamp(self):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.timestamp))

    def get_order_info(self):
        return {
            "Order Number": self.get_order_number(),
            "owner": self.ownerPortfolio.get_owner(),
            "Volume": self.get_volume(),
            "Price": self.get_price(),
            "Side": self.get_side(),
            "Symbol": self.get_symbol(),
            "Timestamp": self.get_formatted_timestamp(),
        }

    # --------- Setter Methods ---------
    def set_owner(self, owner):
        self.owner = owner

    def set_volume(self, volume):
        self.volume = volume

    def set_price(self, price):
        self.price = price

    def set_side(self, side):
        self.side = side

    def set_symbol(self, symbol):
        self.symbol = symbol
