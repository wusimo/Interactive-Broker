# data.py
from pandas.io.data import DataReader
from datetime import datetime
import os, os.path
import pandas as pd
import urllib2
from abc import ABCMeta, abstractmethod

from event import MarketEvent

class DataHandler(object):
    """
        DataHandler is an abstract base class providing an interface for
        all subsequent (inherited) data handlers (both live and historic).
        
        The goal of a (derived) DataHandler object is to output a generated
        set of bars (OLHCVI) for each symbol requested.
        
        This will replicate how a live strategy would function as current
        market data would be sent "down the pipe". Thus a historic and live
        system will be treated identically by the rest of the backtesting suite.
        """
    
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def get_latest_bars(self, symbol, N=1):
        """
            Returns the last N bars from the latest_symbol list,
            or fewer if less bars are available.
            """
        raise NotImplementedError("Should implement get_latest_bars()")
    
    @abstractmethod
    def update_bars(self):
        """
            Pushes the latest bar to the latest symbol structure
            for all symbols in the symbol list.
            """
        raise NotImplementedError("Should implement update_bars()")


class HistoricCSVDataHandler(DataHandler):
    """
        HistoricCSVDataHandler is designed to read CSV files for
        each requested symbol from disk and provide an interface
        to obtain the "latest" bar in a manner identical to a live
        trading interface.
        """
    
    def __init__(self, events, csv_dir, symbol_list):
        """
            Initialises the historic data handler by requesting
            the location of the CSV files and a list of symbols.
            
            It will be assumed that all files are of the form
            'symbol.csv', where symbol is a string in the list.
            
            Parameters:
            events - The Event Queue.
            csv_dir - Absolute directory path to the CSV files.
            symbol_list - A list of symbol strings.
            """
        self.events = events
        self.csv_dir = csv_dir
        self.symbol_list = symbol_list
        
        self.symbol_data = {}
        self.latest_symbol_data = {}
        self.continue_backtest = True
        self._open_convert_csv_files()
    
    
    def _open_convert_csv_files(self):
        """
            Opens the CSV files from the data directory, converting
            them into pandas DataFrames within a symbol dictionary.
            
            For this handler it will be assumed that the data is
            taken from DTN IQFeed. Thus its format will be respected.
            """
        comb_index = None
        for s in self.symbol_list:
            # Load the CSV file with no header information, indexed on date
            self.symbol_data[s] = pd.io.parsers.read_csv(
                                                         os.path.join(self.csv_dir, '%s.csv' % s),
                                                         header=0, index_col=0,
                                                         names=['datetime','open','low','high','close','volume','oi']
                                                         )
                
            # Combine the index to pad forward values
            if comb_index is None:
                comb_index = self.symbol_data[s].index
            else:
                comb_index.union(self.symbol_data[s].index)
                                                                 
            # Set the latest symbol_data to None
            self.latest_symbol_data[s] = []
                                                             
        # Reindex the dataframes
        for s in self.symbol_list:
            self.symbol_data[s] = self.symbol_data[s].reindex(index=comb_index, method='pad').iterrows()


    def _get_new_bar(self, symbol):
        """
            Returns the latest bar from the data feed as a tuple of
            (sybmbol, datetime, open, high, low, close, volume).
            """
        for b in self.symbol_data[symbol]:
            yield tuple([symbol, datetime.strptime(b[0], '%Y-%m-%d'),
                         b[1][0], b[1][1], b[1][2], b[1][3], b[1][4]])
        #used to be:%Y-%m-%d %H:%M:%S
        # Made some change on Jan-3-2016, changed datetime.datetime.strptime to
        # datetime.strptime. Must due to the update of python library
        
        
    def get_latest_bars(self, symbol, N=1):
        """
            Returns the last N bars from the latest_symbol list,
            or N-k if less available.
            """
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print "That symbol is not available in the historical data set."
        else:
            return bars_list[-N:]
    
    
    def update_bars(self):
        """
            Pushes the latest bar to the latest_symbol_data structure
            for all symbols in the symbol list.
            """
        for s in self.symbol_list:
            try:
                bar = self._get_new_bar(s).next()
            except StopIteration:
                self.continue_backtest = False
            else:
                if bar is not None:
                    self.latest_symbol_data[s].append(bar)
        self.events.put(MarketEvent())



class GoogleFinanceAPI:

    def __init__(self):
        self.prefix = "http://www.google.com/finance/getprices?"
    
    
    def get(self,symbol,period,days):
        url = self.prefix+"i=%s&p=%s&&f=d,o,h,l,c,v&df=cpct&q=%s"%(period,days,symbol)
        u = urllib2.urlopen(url)
        content = u.read()
        return content
            
            
            
            
class RealTimeDataHandler(DataHandler):

    def __init__(self,events,symbol_list):# should input symbol or symbol list?
        self.events = events
        self.symbol_list = symbol_list #symbol must contain symbol, section type, exchange
        #self.csv_dir = csv_dir
        self.symbol_data = {}
        self.latest_symbol_data = {}
        #self.continue_backtest = False
        #self._init_download_dataframe()
        for s in self.symbol_list:
            self.latest_symbol_data[s] = []

# Later we will implement the reqMktData Way to retrieve market data
    """
        def _download_datafra
        me(self)
    
        def my_account_handler(msg):
        print(msg)
    
    
        def my_tick_handler(msg):
        print(msg)
    
        con = ibConnection()
        con.register(my_account_handler, 'UpdateAccountValue')
        con.register(my_tick_handler, message.tickSize, message.tickPrice)
        con.connect()
    
        con.reqAccountUpdates(1, '')# not sure what is this doing
        qqqq = Contract()
        qqqq.m_symbol = self.symbol.symbol
        qqqq.m_secType = self.symbol.secType
        qqqq.m_exchange =self.symbol.exchange
        con.reqMktData(1, qqqq, '', False)
        con.disconnect()
        """
        
    def _init_download_dataframe(self):
        
        comb_index = None
        start_date = datetime(2011,12,5)
        end_date = datetime(2011,12,16)

        for s in self.symbol_list:
                        #Retrieving the chart
            self.symbol_data[s] = DataReader(s,'yahoo',start_date,end_date)
            
            # Combine the index to pad forward values
            if comb_index is None:
                comb_index = self.symbol_data[s].index
            else:
                comb_index.union(self.symbol_data[s].index)
            
            # Set the latest symbol_data to None
            self.latest_symbol_data[s] = []
        
        # Reindex the dataframes
        for s in self.symbol_list:
            self.symbol_data[s] = self.symbol_data[s].reindex(index=comb_index, method='pad').iterrows()





    def update_bars(self):
        """
            Pushes the latest bar to the latest_symbol_data structure
            for all symbols in the symbol list.
            """
        for s in self.symbol_list:
            bar = self._get_new_bar(s)
            self.latest_symbol_data[s].append(bar)
        self.events.put(MarketEvent())


    def get_latest_bars(self, symbol, N=1):
        """
            Returns the last N bars from the latest_symbol list,
            or N-k if less available.
            """
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print "That symbol is not available in the historical data set."
        else:
            return bars_list[-N:]




    def _get_new_bar(self,symbol):
        """
            Returns the latest bar from the data feed as a tuple of
            (sybmbol, datetime, open, low, high, close, volume).
            """
        #scrapy here
        c = GoogleFinanceAPI()
        quote = c.get(symbol,"60","1m")
        print(symbol)
        return tuple([symbol, datetime.now(),
                    float(quote.splitlines()[8].split(",")[4]), float(quote.splitlines()[8].split(",")[3]),
                    float(quote.splitlines()[8].split(",")[2]), float(quote.splitlines()[8].split(",")[1]),
                    float(quote.splitlines()[8].split(",")[5])])

