import csv
import os
from . import CommissionService
            
class Transaction:
    def __init__(self, team_name, filename_suffix="transaction_log.csv"):
        self.transaction_log = [] 
        self.team_name = team_name

        folder = os.path.join("result", team_name)
        os.makedirs(folder, exist_ok=True)
        self.csv_file = os.path.join(folder, f"{team_name}_{filename_suffix}")
        
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, mode='w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=[
                    'Order Number', 'owner', 'Volume', 'Price', 'Side', 'Symbol', 'Timestamp'
                ])
                writer.writeheader()
    
    def create_transaction_log(self, order):
        order_info = order.get_order_info()
        if order_info["Side"] == "Buy":
            order_info["Price"] += CommissionService.commissionService._get_slippage(order_info["Price"])
        elif order_info["Side"] == "Sell":
            order_info["Price"] -= CommissionService.commissionService._get_slippage(order_info["Price"])
        
        self.transaction_log.append(order_info)
    
    def flush_logs(self):
        with open(self.csv_file, mode='a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=[
                'Order Number', 'owner', 'Volume', 'Price', 'Side', 'Symbol', 'Timestamp'
            ])
            writer.writerows(self.transaction_log)
