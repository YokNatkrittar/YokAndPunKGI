from abc import ABC, abstractmethod
from datetime import timedelta

class Strategy_template(ABC):
    def __init__(self,owner,strategy_name, handler):
        self.owner = owner
        self.strategy_name = strategy_name
        self.handler = handler

    @abstractmethod
    def on_data(self,row):
        """
        MUST be implement by subclass
        DO NOT EDIT THIS CLASS
        """
        pass
