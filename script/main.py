
# coding: utf-8

# In[3]:

import event, data, strategy, portfolio, execution, time, Queue

mode = "Backtesting"

if mode == "Backtesting":
    ##-------------Initialization-------------------------------------------
    # Declare the components with respective parameters
    events = Queue.Queue()
    
    # You need to change this to your directory
    rootpath = "C:/Users/Ruimin/Anaconda2/IBtrading/"
    symbol_list = ["chart"]
    # (self, events, csv_dir, symbol_list)
    bars = data.HistoricCSVDataHandler(events, rootpath, symbol_list) 

    strategy = strategy.technical_RSI(bars, events) #(self, bars, events)

    # (self, bars, events, start_date, initial_capital=100000.0)
    port = portfolio.NaivePortfolio(bars, events, "12-5-2014", 10000000)  

    broker = execution.SimulatedExecutionHandler(events)

    ##--------------Start backtesting-----------------------------------------
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
                        print "Market Event"
                        port.update_timeindex(event)
                        print "Portfolio Update"

                    elif event.type == 'SIGNAL':
                        port.update_signal(event)
                        print "Portfolio Event"

                    elif event.type == 'ORDER':
                        broker.execute_order(event)
                        print "Order Event"
                        #time.sleep(3) # just to make sure the order could be filled by the broker
                        
                    elif event.type == 'FILL':
                        port.update_fill(event)
                        print "Order Done"
                
        # 1-Second heartbeat, accelerate backtesting
        time.sleep(1)
elif mode == "Realtime":
    print "Let's merge your code here"


# In[ ]:



