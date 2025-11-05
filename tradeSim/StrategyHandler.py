import copy
from types import MappingProxyType

class StrategyHandler:
    def __init__(self, strategy_class, strategy_runner):
        self.strategy = strategy_class(self)
        self._runner = strategy_runner
        self._current_row = None

        self.cum_buy_volume = 0
        self.cum_sell_volume = 0

    def process_row(self, row):
        
        #made deep copy and readonly
        self._current_row = MappingProxyType(copy.deepcopy(dict(row)))

        flag = row["Flag"]
        volume = row["Volume"]
        
        if flag == "Buy":
            self.cum_buy_volume += volume
        elif flag == "Sell":
            self.cum_sell_volume += volume

        self.strategy.on_data(self._current_row)

    def create_order_to_limit(self, volume, price, side, symbol):
        if self._current_row is None:
            raise RuntimeError("There is error in daily tick row data. Please check the data source.")
        return self._runner.create_order_to_limit(volume, price, side, symbol, self.cum_sell_volume, self.cum_buy_volume, self._current_row)
    
    def create_order_at_market(self, volume, side, symbol):
        if self._current_row is None:
            raise RuntimeError("There is error in daily tick row data. Please check the data source.")
        return self._runner.create_order_at_market(volume, side, symbol, self.cum_sell_volume, self.cum_buy_volume, self._current_row)

    def check_port_has_stock(self, symbol, volume):
        return self._runner.check_port_has_stock(symbol, volume)

    def get_owner(self):
        return self._runner.get_owner()
    
    def get_all_stocks_info(self):
        return self._runner.get_all_stocks_info()
    
    def get_portfolio_info(self):
        return self._runner.get_portfolio_info()
    
    def get_stock_by_symbol(self,symbol):
        return self._runner.get_stock_by_symbol(symbol)
    
    def get_total_stock_volume_by_symbol(self, symbol):
        return self._runner.get_total_stock_volume_by_symbol(symbol)
    
    def get_cash_balance(self):
        return self._runner.get_cash_balance()
    
    def get_roi(self):
        return self._runner.get_roi()
    
    def get_max_draw_down(self):
        return self._runner.get_max_draw_down()
    
    def get_number_of_wins(self):
        return self._runner.get_number_of_wins()
    
    def get_number_of_sells(self):
        return self._runner.get_number_of_sells()
