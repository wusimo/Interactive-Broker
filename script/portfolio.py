# portfolio.py

import datetime
import numpy as np
import pandas as pd
import Queue

from abc import ABCMeta, abstractmethod
from math import floor, ceil

from event import FillEvent, OrderEvent
from performance import create_sharpe_ratio, create_drawdowns

class Portfolio(object):
    """
        The Portfolio class handles the positions and market
        value of all instruments at a resolution of a "bar",
        i.e. secondly, minutely, 5-min, 30-min, 60 min or EOD.
        """
    
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def update_signal(self, event):
        """
            Acts on a SignalEvent to generate new orders
            based on the portfolio logic.
            """
        raise NotImplementedError("Should implement update_signal()")
    
    @abstractmethod
    def update_fill(self, event):
        """
            Updates the portfolio current positions and holdings
            from a FillEvent.
            """
        raise NotImplementedError("Should implement update_fill()")



class NaivePortfolio(Portfolio):
    """
        The NaivePortfolio object is designed to send orders to
        a brokerage object with a constant quantity size blindly,
        i.e. without any risk management or position sizing. It is
        used to test simpler strategies such as BuyAndHoldStrategy.
        """
    
    def __init__(self, bars, events, start_date, initial_capital=100000.0):
        """
            Initialises the portfolio with bars and an event queue.
            Also includes a starting datetime index and initial capital
            (USD unless otherwise stated).
            
            Parameters:
            bars - The DataHandler object with current market data.
            events - The Event Queue object.
            start_date - The start date (bar) of the portfolio.
            initial_capital - The starting capital in USD.
            """
        self.bars = bars
        self.events = events
        self.symbol_list = self.bars.symbol_list
        self.start_date = start_date
        self.initial_capital = initial_capital
        
        self.all_positions = self.construct_all_positions()
        self.current_positions = dict( (k,v) for k, v in [(s, 0) for s in self.symbol_list] )
        
        self.all_holdings = self.construct_all_holdings()
        self.current_holdings = self.construct_current_holdings()
    
    
    def construct_all_positions(self):
        """
            Constructs the positions list using the start_date
            to determine when the time index will begin.
            """
        d = dict( (k,v) for k, v in [(s, 0) for s in self.symbol_list] )
        d['datetime'] = self.start_date
        return [d]
    
    
    def construct_all_holdings(self):
        """
            Constructs the holdings list using the start_date
            to determine when the time index will begin.
            """
        d = dict( (k,v) for k, v in [(s, 0.0) for s in self.symbol_list] )
        d['datetime'] = self.start_date
        d['cash'] = self.initial_capital
        d['commission'] = 0.0
        d['total'] = self.initial_capital
        return [d]
    
    def construct_current_holdings(self):
        """
            This constructs the dictionary which will hold the instantaneous
            value of the portfolio across all symbols.
            """
        d = dict( (k,v) for k, v in [(s, 0.0) for s in self.symbol_list] )
        d['cash'] = self.initial_capital
        d['commission'] = 0.0
        d['total'] = self.initial_capital
        return d
    
    def update_timeindex(self, event):
        """
            Adds a new record to the positions matrix for the current
            market data bar. This reflects the PREVIOUS bar, i.e. all
            current market data at this stage is known (OLHCVI).
            
            Makes use of a MarketEvent from the events queue.
            """
        bars = {}
        for sym in self.symbol_list:
            bars[sym] = self.bars.get_latest_bars(sym, N=1)
    
        # Update positions
        dp = dict( (k,v) for k, v in [(s, 0) for s in self.symbol_list] )
        dp['datetime'] = bars[self.symbol_list[0]][0][1]
        
        for s in self.symbol_list:
            dp[s] = self.current_positions[s]

        # Append the current positions
        self.all_positions.append(dp)
    
        # Update holdings
        dh = dict( (k,v) for k, v in [(s, 0) for s in self.symbol_list] )
        dh['datetime'] = bars[self.symbol_list[0]][0][1]
        dh['cash'] = self.current_holdings['cash']
        dh['commission'] = self.current_holdings['commission']
        dh['total'] = self.current_holdings['cash']
        
        for s in self.symbol_list:
            # Approximation to the real value
            market_value = self.current_positions[s] * bars[s][0][5]
            dh[s] = market_value
            dh['total'] += market_value

        # Append the current holdings
        self.all_holdings.append(dh)


    def update_positions_from_fill(self, fill):
        """
            Takes a FilltEvent object and updates the position matrix
            to reflect the new position.
        
            Parameters:
            fill - The FillEvent object to update the positions with.
            """
        # Check whether the fill is a buy or sell
        fill_dir = 0
        if fill.direction == 'BUY':
            fill_dir = 1
        if fill.direction == 'SELL':
            fill_dir = -1
                                
        # Update positions list with new quantities
        self.current_positions[fill.symbol] += fill_dir*fill.quantity


    def update_holdings_from_fill(self, fill):
        """
            Takes a FillEvent object and updates the holdings matrix
            to reflect the holdings value.
        
            Parameters:
            fill - The FillEvent object to update the holdings with.
            """
        # Check whether the fill is a buy or sell
        fill_dir = 0
        if fill.direction == 'BUY':
            fill_dir = 1
        if fill.direction == 'SELL':
            fill_dir = -1
                                
        # Update holdings list with new quantities
        fill_cost = self.bars.get_latest_bars(fill.symbol)[0][5]  # Close price
        cost = fill_dir * fill_cost * fill.quantity
        self.current_holdings[fill.symbol] += cost
        self.current_holdings['commission'] += fill.commission
        self.current_holdings['cash'] -= (cost + fill.commission)
        self.current_holdings['total'] -= (cost + fill.commission)


    def update_fill(self, event):
        """
            Updates the portfolio current positions and holdings
            from a FillEvent.
            """
        if event.type == 'FILL':
            self.update_positions_from_fill(event)
            self.update_holdings_from_fill(event)
        
        
    def generate_naive_order(self, signal):
        """
            Simply transacts an OrderEvent object as a constant quantity
            sizing of the signal object, without risk management or
            position sizing considerations.
            
            Parameters:
            signal - The SignalEvent signal information.
            """
        order = None
        
        symbol = signal.symbol
        direction = signal.signal_type
        strength = signal.strength
        

        if strength == "strong":
            mkt_quantity = 10
        elif strength == "mild":
            mkt_quantity = 5
        elif strength == "weak":
            mkt_quantity = 2
        
        #mkt_quantity = floor(100 * strength)  
        cur_quantity = self.current_positions[symbol]
        order_type = 'MKT'
        
        if direction == 'LONG' and cur_quantity == 0:
            order = OrderEvent(symbol, order_type, mkt_quantity, 'BUY')
        if direction == 'SHORT' and cur_quantity == 0:
            order = OrderEvent(symbol, order_type, mkt_quantity, 'SELL')
        
        if direction == 'EXIT' and cur_quantity > 0:
            order = OrderEvent(symbol, order_type, abs(cur_quantity), 'SELL')
        if direction == 'EXIT' and cur_quantity < 0:
            order = OrderEvent(symbol, order_type, abs(cur_quantity), 'BUY')
        return order


    def generate_simple_order(self, signal):
        """
        A little more complicated than the naive one. The order size is decided based
        on the following criterion
        1. For any security, its holding proportion cannot exceed 40 percent of the total capital
        2. For cash, we always make sure it accounts for at least 30 percent of the total capital
        3. Only send Market order
        """
        order = None
        
        symbol = signal.symbol
        direction = signal.signal_type
        strength = signal.strength

        ## Decide order size
        # First stage: only consider signal strength
        if strength == "strong":
            mkt_quantity = 10
        elif strength == "mild":
            mkt_quantity = 5
        elif strength == "weak":
            mkt_quantity = 2

        cur_position = self.current_positions[symbol]
        cur_holding = self.current_holdings[symbol]
        cur_capital = self.all_holdings[-1]['total']    

        if cur_position != 0:
            # Second stage: make sure absolute holding of the current security
            # does not exceed 40 percent of the total capital
            if direction == "LONG":
                tmp_position = cur_position + mkt_quantity
            elif direction == "SHORT":
                tmp_position = cur_position - mkt_quantity

            tmp_holding = float(tmp_position) / cur_position * cur_holding
            tmp_ratio = tmp_holding / cur_capital # do not consider commission here, and assume no slippage
                                                   # so capital won't change, equals to current capital
            if tmp_ratio > 0.4:
                mkt_quantity = floor(tmp_position * 0.4 / tmp_ratio) - cur_position # this order quantity will
                                                                                    # make the proportion close
                                                                                    # to 40%
            elif tmp_ratio < -0.4:
                mkt_quantity = cur_position - ceil(tmp_position * 0.4 / abs(tmp_ratio)) # same as above


            # Third stage: make sure cash accounts at least 30 percent of the total capital
            # since if we are shorting, cash will always increase, so only need to check the
            # "longing" situation
            if direction == "LONG":
                cur_cash = self.all_holdings[-1]['cash']
                tmp_cash = cur_cash - mkt_quantity/cur_position*cur_holding

                tmp_ratio = tmp_cash / cur_capital
                if tmp_ratio < 0.3:
                    # this order quantity will make the cash accounts close to 30% of the total capital
                    mkt_quantity = floor((cur_cash - cur_capital*0.3) * (cur_position / cur_holding))


        ## Generate order
        order_type = 'MKT'

        if direction == 'LONG':
            order = OrderEvent(symbol, order_type, mkt_quantity, 'BUY')
        elif direction == 'SHORT':
            order = OrderEvent(symbol, order_type, mkt_quantity, 'SELL')

        return order




    def update_signal(self, event):
        """
            Acts on a SignalEvent to generate new orders
            based on the portfolio logic.
            """
        if event.type == 'SIGNAL':
            order_event = self.generate_simple_order(event)
            self.events.put(order_event)
        
        
    def create_equity_curve_dataframe(self):
        """
            Creates a pandas DataFrame from the all_holdings
            list of dictionaries.
            """
        curve = pd.DataFrame(self.all_holdings)
        curve.set_index('datetime', inplace=True)
        curve['returns'] = curve['total'].pct_change()
        curve['equity_curve'] = (1.0+curve['returns']).cumprod()
        self.equity_curve = curve

    def output_summary_stats(self):
        """
            Creates a list of summary statistics for the portfolio such
            as Sharpe Ratio and drawdown information.
            """
        total_return = self.equity_curve['equity_curve'][-1]
        returns = self.equity_curve['returns']
        pnl = self.equity_curve['equity_curve']
                        
        sharpe_ratio = create_sharpe_ratio(returns)
        max_dd, dd_duration = create_drawdowns(pnl)
                                
        stats = [("Total Return", "%0.2f%%" % ((total_return - 1.0) * 100.0)),
                ("Sharpe Ratio", "%0.2f" % sharpe_ratio),
                ("Max Drawdown", "%0.2f%%" % (max_dd * 100.0)),
                ("Drawdown Duration", "%d" % dd_duration)]
        return stats
