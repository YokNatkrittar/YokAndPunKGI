import time
import datetime
import inspect


class stock:
    def __init__(
        self,
        symbol,
        start_vol,
        buy_price,
        mkt_price,
        buytime,
        amount_cost=0.0,
        avg_cost=0.0,
        market_value=0.0,
        unrealized=0.0,
        unrealizedInPercentage=0.0,
        realized=0.0,
    ):
        self.symbol = symbol
        self.start_vol = start_vol
        self.actual_vol = start_vol
        self.buy_price = buy_price
        self.mkt_price = mkt_price
        self.amount_cost = amount_cost
        self.avg_cost = avg_cost
        self.market_value = market_value
        self.unrealized = unrealized
        self.unrealizedInPercentage = unrealizedInPercentage
        self.realized = realized
        self.buy_time = buytime

    def updateStockMk_value(self, mkt_price, avg_cost):
        self.mkt_price = mkt_price
        self.avg_cost = avg_cost
        self.__calAmount_Cost(avg_cost)
        self.__calMarket_value()
        self.__calUnrealized()
        self.__calUnrealizedInPercentage()

    def decreaseStockVolume(self, volume):
        caller = inspect.stack()[1].function
        if caller != "decrease_stock_volume":
            raise ValueError(f"decrease stock volume must be called from decrease_stock_volume(). unable to decrease stock volume from {caller}()")
        if volume < 0:
            raise ValueError("Volume must be positive.")
        self.actual_vol -= volume

    def get_stock_info(self):
        return {
            "Symbol": self.symbol,
            "Actual Volume": self.actual_vol,
            "Buy Price": round(self.buy_price, 2),
            "Market Price": round(self.mkt_price, 2),
            "Average Cost": round(self.avg_cost, 2),
            "Amount Cost": round(self.amount_cost, 2),
            "Market Value": round(self.market_value, 2),
            "Unrealized P&L": round(self.unrealized, 2),
            "Unrealized %": round(self.unrealizedInPercentage, 2),
            "Realized P&L": round(self.realized, 2),
            "Buy time": self.get_buy_time_str(),
        }

    def __calAmount_Cost(self, Symbol_avg_cost):
        self.amount_cost = self.actual_vol * Symbol_avg_cost

    def __calMarket_value(self):
        self.market_value = self.actual_vol * self.mkt_price

    def __calUnrealized(self):
        self.unrealized = self.market_value - self.amount_cost

    def __calUnrealizedInPercentage(self):
        self.unrealizedInPercentage = (
            (self.unrealized / self.amount_cost) * 100 if self.amount_cost != 0 else 0.0
        )

    def add_realized(self, realized):
        caller = inspect.stack()[1].function
        if caller != "decrease_stock_volume":
            raise ValueError(f"add_realized must be called from decrease_stock_volume(). unable to add stock from {caller}()")
        self.realized += realized

    # Getter methods
    def get_symbol(self):
        return self.symbol

    def get_buy_price(self):
        return self.buy_price

    def get_start_vol(self):
        return self.start_vol

    def get_actual_vol(self):
        return self.actual_vol

    def get_mkt_price(self):
        return self.mkt_price

    def get_amount_cost(self):
        return self.amount_cost

    def get_market_value(self):
        return self.market_value

    def get_unrealized(self):
        return self.unrealized

    def get_unrealized_in_percentage(self):
        return self.unrealizedInPercentage

    def get_realized(self):
        return self.realized

    def get_buy_time_str(self):
        return datetime.datetime.fromtimestamp(self.buy_time).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    def to_dict(self):
        return {
            "symbol": self.symbol,
            "buy_price": self.buy_price,
            "actual_vol": self.actual_vol,
            "start_vol": self.start_vol,
            "buy_time": self.buy_time,
            "amount_cost": self.amount_cost,
            "market_value": self.market_value,
            "unrealized": self.unrealized,
            "realized": self.realized,
        }

    @classmethod
    def from_dict(cls, data):
        stock = cls(
            symbol=data["symbol"],
            start_vol=int(data["start_vol"]),
            buy_price=float(data["buy_price"]),
            buytime=data["buy_time"],
            amount_cost=float(data["amount_cost"]),
            market_value=float(data["market_value"]),
            unrealized=float(data["unrealized"]),
            mkt_price=float(data["market_value"])/float(data["start_vol"]),
            realized=float(data["realized"]),
        )

        stock.actual_vol = int(data.get("actual_vol", data["start_vol"]))
        return stock
