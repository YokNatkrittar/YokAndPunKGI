from strategy.Strategies_template import Strategy_template

class YokAndPun_strategy(Strategy_template):
    def __init__(self, handler):
        super().__init__("YokAndPun", "YokAndPun_strategy", handler)
        
        self.INITIAL_STOCKS = [
    "ADVANC",
    "AOT",
    "AWC",
    "BANPU",
    "BBL",
    "BCP",
    "BDMS",
    "BEM",
    "BH",
    "BJC",
    "BTS",
    "CBG",
    "CCET",
    "COM7",
    "CPALL",
    "CPF",
    "CPN",
    "CRC",
    "DELTA",
    "EGCO",
    "GPSC",
    "GULF",
    "HMPRO",
    "IVL",
    "KBANK",
    "KKP",
    "KTB",
    "KTC",
    "LH",
    "MINT",
    "MTC",
    "OR",
    "OSP",
    "PTT",
    "PTTEP",
    "PTTGC",
    "RATCH",
    "SCB",
    "SCC",
    "SCGP",
    "TCAP",
    "TIDLOR",
    "TISCO",
    "TLI",
    "TOP",
    "TRUE",
    "TTB",
    "TU",
    "VGI",
    "WHA"
]
        # ["ADVANC", "SCB", "KBANK", "PTT", "CPN"]
    
        self.MAX_POSITIONS_PER_STOCK = 5 # จำกัดการซื้อสูงสุด 5 ครั้ง (500 หุ้น) ต่อตัว
        
        # ตัวแปรสำหรับกลยุทธ์ Mean Reversion
        self.EMA_ALPHA = 0.2  # Smoothing factor สำหรับ EMA (ค่าสูง = ตอบสนองเร็ว)
        self.EMA_DICT = {s: 0.0 for s in self.INITIAL_STOCKS} # เก็บค่า EMA ล่าสุด
        self.BUY_THRESHOLD = 0.005 # ซื้อเมื่อราคาต่ำกว่า EMA 0.5%
        
        # ค่าคงที่สำหรับค่าธรรมเนียมและการขาย
        self.TOTAL_FEE_RATE = 0.00157 * 1.07 
        self.MAX_LOSS_PERCENT = 0.025

    def on_data(self, row):
        symbol = row['ShareCode']
        price = row['LastPrice']
        volume_to_trade = 100
        
        # 0. อัปเดต EMA สำหรับหุ้นตัวนี้
        if symbol in self.EMA_DICT:
            current_ema = self.EMA_DICT[symbol]
            if current_ema == 0.0:
                 # เริ่มต้น EMA ด้วยราคาแรก
                self.EMA_DICT[symbol] = price
            else:
                 # คำนวณ EMA: New EMA = Alpha * Price + (1 - Alpha) * Old EMA
                self.EMA_DICT[symbol] = (self.EMA_ALPHA * price) + ((1 - self.EMA_ALPHA) * current_ema)

        # 1. ตรวจสอบเงื่อนไขการซื้อ: Buy the Dip
        
        # A. ตรวจสอบว่าหุ้นอยู่ในรายการที่เราสนใจหรือไม่
        if symbol in self.INITIAL_STOCKS:
            
            # B. ตรวจสอบว่าจำนวนหุ้นที่ถืออยู่ **ยังไม่เต็ม**
            current_volume = self.handler.get_total_stock_volume_by_symbol(symbol)
            if current_volume < (self.MAX_POSITIONS_PER_STOCK * volume_to_trade):
                
                current_ema = self.EMA_DICT.get(symbol, 0.0)
                
                # C. ตรวจสอบเงื่อนไขการเข้าซื้อ (ราคาปัจจุบันต่ำกว่า EMA ที่ -0.5%)
                if current_ema > 0.0 and price < current_ema * (1 - self.BUY_THRESHOLD):
                    
                    # ใช้ Limit Order เพื่อควบคุมราคาซื้อ
                    # ตั้งราคา Limit ที่ราคาปัจจุบันเพื่อเพิ่มโอกาสในการจับคู่ทันที
                    order_result = self.handler.create_order_to_limit(volume_to_trade, price, "Buy", symbol)
                    
                    if isinstance(order_result, str) and "[ERROR]" not in order_result:
                         print(f"BUY {symbol} at {price:.2f}. Dip triggered (Price < EMA - 0.5%)")
                    # Note: ไม่ต้องใช้ self.bought_initial แล้ว เพราะการซื้อเกิดขึ้นเรื่อยๆ

        # 2. ตรรกะการขาย (Take Profit และ Stop Loss)
        
        # ดึงข้อมูล Positions ที่ถืออยู่ (In-Memory)
        stocks_held = self.handler.get_stock_by_symbol(symbol)
        
        if stocks_held and self.handler.check_port_has_stock(symbol, volume_to_trade):

            for stock in stocks_held:
                buy_price = stock.get_buy_price()
                
                # คำนวณ Thresholds
                net_break_even_price = buy_price * (1 + self.TOTAL_FEE_RATE) / (1 - self.TOTAL_FEE_RATE)
                take_profit_threshold = net_break_even_price * 1.0025 # 1% กำไร
                stop_loss_threshold = buy_price * (1 - self.MAX_LOSS_PERCENT) * (1 - self.TOTAL_FEE_RATE)

                
                # 🚀 Take Profit
                if price > take_profit_threshold:
                    self.handler.create_order_to_limit(volume_to_trade, price, "Sell", symbol)
                    print(f"TP: {symbol} at {price:.2f}. Buy: {buy_price:.2f}")

                # 🛑 Stop Loss
                elif price < stop_loss_threshold:
                    self.handler.create_order_at_market(volume_to_trade, "Sell", symbol)
                    print(f"SL: {symbol} at {price:.2f}. Buy: {buy_price:.2f}")