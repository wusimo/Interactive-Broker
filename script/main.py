# Declare the components with respective parameters
import sys

# You need to change this to your directory
sys.path.append("Users/Simo/Documents/Interactive-Broker/IbPy")

import event,data,strategy,portfolio,execution,time,Queue

events ＝ Queue.Queue()
events.put(MarketEvent())
symbol_list = ["IBM"]
bars = DataHandler(events,"",symbol_list)   #(self, events, csv_dir, symbol_list)
strategy = Strategy(bars,events) #(self, bars, events)
port = Portfolio(bars,events,)   #(self, bars, events, start_date, initial_capital=100000.0)
broker = ExecutionHandler(..)

while True:
    # Update the bars (specific backtest code, as opposed to live trading)
    if bars.continue_backtest == True:
        bars.update_bars()
    else:
        break

    # Handle the events
    while True:
        try:
            event = events.get(False)
        except Queue.Empty:
            break
        else:
            if event is not None:
                if event.type == 'MARKET':
                    strategy.calculate_signals(event)
                    port.update_timeindex(event)
                
                elif event.type == 'SIGNAL':
                    port.update_signal(event)
                
                elif event.type == 'ORDER':
                    broker.execute_order(event)
                
                elif event.type == 'FILL':
                    port.update_fill(event)

# 10-Minute heartbeat
time.sleep(10*60)