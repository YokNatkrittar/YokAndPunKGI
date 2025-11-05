import unittest
from tradeSim  import Portfolio
from tradeSim  import Stock
import time

class TestPortfolioMethod(unittest.TestCase):

    def setUp(self):
        #init set up for every test
        self.portfolio = Portfolio.portfolio("User 1")

    def test_init_stock(self):
        self.assertIsNotNone(self.portfolio)

    def test_add_stock_direct_call_raises_error(self):
        stock = Stock.stock("AOT", 200, 30.0, 28.9, time.time())

        with self.assertRaises(ValueError) as context:
            self.portfolio.add_stock(stock)

        self.assertIn(
            "add stock must be called from create_order()",
            str(context.exception)
        )
    
    def test_direct_decreaseStockVolume_call_raises_error(self):
        stock = Stock.stock("AOT", 200, 30.0, 28.9, time.time())
        
        # Bypass portfolio to test direct call
        with self.assertRaises(ValueError) as context:
            stock.decreaseStockVolume(50)
        
        self.assertIn(
            "decrease stock volume must be called from decrease_stock_volume()",
            str(context.exception)
        )
    
if __name__ == '__main__':
    unittest.main() 