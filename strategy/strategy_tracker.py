import pandas as pd
import os
# Removed 'import inspect'
# Use os.getcwd() and relative path based on the simulation root

class StrategyTracker:
    def __init__(self, team_name, strategy_name):
        # 1. Define the log directory relative to the project root (where the main notebook runs)
        self.log_dir = './strategy_logs'
        
        # 2. Use the simplified relative path for the filename
        self.filename = os.path.join(self.log_dir, f'{team_name}_{strategy_name}_tracker.csv')
        self.columns = ['Symbol', 'BuyPrice', 'Volume', 'BuyTime']
        
        # 3. Ensure the directory exists (must be called before loading/saving)
        # This will create strategy_logs/ in the main directory
        os.makedirs(self.log_dir, exist_ok=True)
        
        self.data = pd.DataFrame(columns=self.columns)
        self._load_data()

    def _load_data(self):
        """Loads existing data from CSV, handling empty or corrupt files gracefully."""
        # 1. Check if file exists
        if os.path.exists(self.filename):
            # 2. Check if file is empty (0 bytes)
            if os.path.getsize(self.filename) == 0:
                print(f"Tracker file is empty. Starting fresh.")
                self.data = pd.DataFrame(columns=self.columns)
                return
            
            # 3. If file is not empty, attempt to read it
            try:
                self.data = pd.read_csv(self.filename, keep_default_na=False)
            except Exception as e:
                # Catches errors like 'No columns to parse'
                print(f"Error loading tracker data: {e}. Starting fresh.")
                self.data = pd.DataFrame(columns=self.columns)
        
    def _save_data(self):
        """Saves the current DataFrame to the CSV file, overwriting the old one."""
        # Use mode='w' to ensure it completely overwrites and flushes the file.
        self.data.to_csv(self.filename, index=False, mode='w') 

    def add_position(self, symbol, buy_price, volume, buy_time):
        """Adds a new bought lot to the tracker and saves. Fixed to resolve FutureWarning."""
        new_row_data = {
            'Symbol': symbol, 
            'BuyPrice': buy_price, 
            'Volume': volume, 
            'BuyTime': buy_time
        }
        new_row = pd.DataFrame([new_row_data])
        
        # Fix for FutureWarning: Explicitly handle the empty DataFrame case.
        if self.data.empty:
            self.data = new_row
        else:
            self.data = pd.concat([self.data, new_row], ignore_index=True)
            
        self._save_data() # Save after adding

    def get_oldest_position(self, symbol):
        """Retrieves the oldest 100-share lot for a given symbol."""
        # Filter for the symbol and a volume of 100
        filtered = self.data[(self.data['Symbol'] == symbol) & (self.data['Volume'] == 100)]
        if not filtered.empty:
            return filtered.iloc[0]
        return None

    def remove_position(self, index):
        """Removes a position by its DataFrame index (after it's sold) and saves."""
        if index in self.data.index:
            self.data.drop(index, inplace=True)
            self.data.reset_index(drop=True, inplace=True)
            self._save_data() # Save after removing
            return True
        return False