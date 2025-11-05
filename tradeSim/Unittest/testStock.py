import unittest
from tradeSim import Stock
import time

class TestStockMethods(unittest.TestCase):

    def test_init_stock(self):
        stock = Stock.stock("AOT", 100, 30.0  , 28.9 , time.time())
        self.assertIsNotNone(stock)

    def test_update_stock_missing_avg_cost(self):
        stock = Stock.stock("AOT", 100, 30.0, 28.0, time.time())

        with self.assertRaises(TypeError):
            stock.updateStockMk_value(mkt_price=30.0)  # missing avg_cost

    def test_update_stock(self):
        stock = Stock.stock("AOT", 100, 30.0, 28.0, time.time())
        stock.updateStockMk_value(mkt_price=30.0, avg_cost= 28.9)  

        self.assertEqual(stock.mkt_price, 30.0)
        self.assertEqual(stock.avg_cost, 28.9)

    def test_decreaseStockVolume_direct_call_raises(self):
        stock = Stock.stock("AOT", 300, 30.0, 28.0, time.time())

        with self.assertRaises(ValueError) as context:
            stock.decreaseStockVolume(200)

        self.assertIn(
            "decrease stock volume must be called from decrease_stock_volume()",
            str(context.exception)
        )

    def test_decreaseStockVolume_with_negative_value_raises_error(self):
        stock = Stock.stock("AOT", 300, 30.0, 28.0, time.time())

        with self.assertRaises(ValueError):
            stock.decreaseStockVolume(-300)

    def test_calAmount_Cost(self):
        stock = Stock.stock("AOT", start_vol= 100, mkt_price= 30.0, buy_price= 28.0, buytime=time.time())
        stock.updateStockMk_value(mkt_price= 30,avg_cost= 28.0)
        self.assertEqual(stock.get_amount_cost(), 2800.0)

    def test_calMarket_value(self):
        stock = Stock.stock("AOT", start_vol= 100, mkt_price= 30.0, buy_price= 28.0, buytime=time.time())
        stock.updateStockMk_value(mkt_price= 30,avg_cost= 28.0)
        self.assertEqual(stock.get_market_value(), 100 * 30.0)  # actual_vol * mkt_price = 2800.0

    def test_calUnrealized(self):
        stock = Stock.stock("AOT", start_vol= 100, mkt_price= 28.0, buy_price= 27.0, buytime=time.time())
        stock.updateStockMk_value(mkt_price= 28,avg_cost= 27.0)
        self.assertEqual(stock.get_unrealized(), 100.0)

    def test_calUnrealizedInPercentage(self):
        stock = Stock.stock("AOT", start_vol= 100, mkt_price= 28.0, buy_price= 27.0, buytime=time.time())
        stock.updateStockMk_value(mkt_price= 28,avg_cost= 27.0)
        self.assertAlmostEqual(stock.get_unrealized_in_percentage(), (100 / 2700) * 100, places=2)

    def test_unrealized_percentage_zero_cost(self):
        # Simulate a case where amount_cost is 0 (e.g., actual_vol = 0)
        stock = Stock.stock("AOT", start_vol=0, mkt_price=28.0, buy_price=27.0, buytime=time.time())
        stock.updateStockMk_value(mkt_price=28.0, avg_cost=27.0)
        self.assertEqual(stock.get_unrealized_in_percentage(), 0.0)

    # def test_calAmount_Cost_with_negative_volume(self):
    #     self.stock.actual_vol = -100
    #     self.stock.calAmount_Cost(28.0)
    #     self.assertEqual(self.stock.amount_cost, -2800.0)  # Should this be allowed? Maybe you want to prevent this

    def test_calUnrealized_negative_cost(self):
        stock = Stock.stock("AOT", start_vol=100, mkt_price=28.0, buy_price=-28.0, buytime=time.time())
        stock.updateStockMk_value(mkt_price=28.0, avg_cost=-28.0)
        self.assertEqual(stock.get_unrealized(), 2800 - (-2800))

    # def test_set_avg_cost_invalid_type(self):
    #     stock = Stock.stock("AOT", start_vol=100, mkt_price=28.0, buy_price=27.0, buytime=time.time())
        
    #     with self.assertRaises(TypeError):
    #         stock.set_avg_cost("invalid")  # avg_cost should be float, you might want to validate that in your code

if __name__ == '__main__':
    unittest.main()