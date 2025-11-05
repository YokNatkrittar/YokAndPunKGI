import unittest
import time
from tradeSim import Execution as Execution
from tradeSim import Portfolio
from tradeSim import Order
from tradeSim import Stock
from tradeSim import CommissionService
import pandas as pd

class testComService(unittest.TestCase):
    

    def test_cal_all_volume_commission_and_vat(self):
        commissionService = CommissionService.commissionService
        cost = commissionService.cal_All_Volume_commissionAndVat(100, 30)
        self.assertGreater(cost, 3000)  # Should be higher than raw price due to comm and VAT


#TODO: test all partitioning
    def test_buy_cal_unit_cost_with_commission(self):
        buy_price = 30 + (0.25)
        amount = buy_price *100
        comm = amount * 0.00157
        caled_vat = comm * 0.07
        result = (buy_price * 100) + comm + caled_vat
        result_per_unit = result/100

        commissionService = CommissionService.commissionService
        unit_cost = commissionService.cal_commissionAndVat(100, 30,'Buy')
        self.assertEqual(unit_cost, result_per_unit)
        
#TODO: test all partitioning
    def test_sell_cal_unit_cost_with_commission(self):
        buy_price = 30 - .25
        amount = buy_price *100
        comm = amount * 0.00157
        caled_vat = comm * 0.07
        result = (buy_price * 100) - comm - caled_vat
        result_per_unit = result/100

        commissionService = CommissionService.commissionService
        unit_cost = commissionService.cal_commissionAndVat(100, 30,'Sell')
        self.assertEqual(unit_cost, result_per_unit)

    def test_wrong_format_cal_unit_cost_with_commission(self):
        commissionService = CommissionService.commissionService
        result = commissionService.cal_commissionAndVat(100, 30, 'not exist condition')
        self.assertIsNone(result)
        
    def test_slippage1(self):
        commissionService = CommissionService.commissionService
        test_cases = [
            (100, 0.1, 0.110184789),
            (100, 0.5, 0.510856749),
            (100, 0.9, 0.911528709),
            (100, 1, 1.011696699),
            (100, 1.1, 1.111864689),
            (100, 1.5, 1.512536649),
            (100, 1.9, 1.913208609),
            (100, 2, 2.023393398),
            (100, 2.1, 2.123561388),
            (100, 2.5, 2.524233348),
            (100, 3.9, 3.926585208),
            (100, 4.5, 4.527593148),
            (100, 5, 5.058483495),
            (100, 8.6, 8.664531135),
            (100, 9.9, 9.966715005),
            (100, 10, 10.11696699),
            (100, 15.5, 15.62620644),
            (100, 24.5, 24.64132554),
            (100, 25, 25.29241748),
            (100, 60, 60.35121398),
            (100, 99, 99.41673008),
            (100, 100, 100.66883),
            (100, 150, 150.752825),
            (100, 199, 199.8351401),
            (100, 200, 201.3376599),
            (100, 250, 251.4216549),
            (100, 399, 400.67196),
            (100, 400, 402.6753198),
            (100, 450, 452.7593148),
        ]

        side = 'Buy'

        for volume, price, expected_unitcost in test_cases:
            with self.subTest(volume=volume, price=price):
                unitcost = commissionService.cal_commissionAndVat(volume=volume, price=price, side=side)
                self.assertAlmostEqual(unitcost, expected_unitcost, places=5)
        

if __name__ == '__main__':
    unittest.main()