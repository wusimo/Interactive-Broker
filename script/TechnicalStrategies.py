from strategy import Strategy
from event import SignalEvent

class RSI(Strategy):
    """
    Relative Strength Index strategy 
    """

    def __init__(self, bars, events):
        """
        Initialises the strategy,
        Params:
        bars: The DataHandler object that provides bar information
        events: The Event Queue object
        """
        self.bars = bars
        self.symbol_list = self.bars.symbol_list
        self.events = events

        # Initialize the holding status to False
        self.bought = self._calculate_initial_bought()


    def _calculate_initial_bought(self):
        """
        Set the holding status to False for all symbols
        """
        bought = {}
        for s in self.symbol_list:
            bought[s] =  False
        return bought

 
    def calculate_signals(self, event, periods=12):
        """
        params:
        event: 
        periods: parameter of RSI, number of periods 
        """
        if event.type == "MARKET":
            for s in self.symbol_list:
                bars = self.bars.get_latest_bars(s, periods+1)
                # Wait until at least "periods"+1 time periods market data is available
                if len(bars) == periods+1:
                    # Calculate RSI
                    close_price = [x[5] for x in bars] # close price for "periods"+1 periods
                    close_price_diff = [close_price[i] - close_price[i-1] for i in range(1, periods+1)]
                    ups_ = [x for x in close_price_diff if x > 0]
                    drops_ = [x for x in close_price_diff if x < 0]
                    ups_total = sum(ups_)
                    drops_total = sum(drops_)

                    if drops_total == 0 and ups_total == 0: # close prices for the last "periods" + 1 periods
                                                            # haven't changed at all. Do not send signal, wait
                        RSI = 50 
                    elif drops_total == 0 and ups_total != 0:
                        RSI = 100
                    else:
                        RS = ups_total / drops_total
                        RSI = 100 * RS/(1+RS) # This is the RSI

                    # Calculate the direction and strenght of the signal
                    if RSI >= 70 and RSI < 80:
                        signal = SignalEvent(bars[0][0], bars[0][1], 'SHORT', "weak")
                    elif RSI >= 80 and RSI < 90:
                        signal = SignalEvent(bars[0][0], bars[0][1], 'SHORT', "mild")
                    elif RSI >= 90:
                        signal = SignalEvent(bars[0][0], bars[0][1], 'SHORT', "strong")
                    elif RSI <= 30 and RSI > 20:
                        signal = SignalEvent(bars[0][0], bars[0][1], 'LONG', "weak")
                    elif RSI <= 20 and RSI > 10:
                        signal = SignalEvent(bars[0][0], bars[0][1], 'LONG', "mild")
                    elif RSI <= 10:
                        signal = SignalEvent(bars[0][0], bars[0][1], 'LONG', "strong")

                    # Only when RSI is less than or equal to 30, or greater than or equal to
                    # 70, a trading signal will be triggered
                    if RSI <= 30 or RSI >= 70:
                        self.events.put(signal)