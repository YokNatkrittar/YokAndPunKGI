import bisect


class commissionService:

    comm = 0.00157
    vat = 0.07
    slippages = [0.01, 0.02, 0.05, 0.10, 0.25, 0.50, 1.00, 2.00]
    price_range = [    2,    5,    10,   25,   100,  200,  400]

    @classmethod
    def _get_slippage(cls, price: float) -> float:
        index = bisect.bisect(cls.price_range, price)
        return cls.slippages[index]

    @classmethod
    def verify_transaction(cls, volume, price, cashBalance):
        return cashBalance >= cls.cal_All_Volume_commissionAndVat(volume, price)

    @classmethod
    def cal_All_Volume_commissionAndVat(cls, volume, price):
        match_price = price + cls._get_slippage(price)
        amount = match_price * volume
        comm_amount = amount * cls.comm
        vat = comm_amount * cls.vat
        return amount + comm_amount + vat

    @classmethod
    def cal_commissionAndVat(cls, volume, price, side):
        if side == "Buy":
            match_price = price + cls._get_slippage(price)
            amount = match_price * volume
            comm_amount = amount * cls.comm
            vat = comm_amount * cls.vat
            return (amount + comm_amount + vat) / volume
        elif side == "Sell":
            match_price = price - cls._get_slippage(price)
            amount = match_price * volume
            comm_amount = amount * cls.comm
            vat = comm_amount * cls.vat
            return (amount - comm_amount - vat) / volume
