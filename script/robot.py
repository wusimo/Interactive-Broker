from ib.opt import Connection, message
from ib.ext.Contract import Contract
from ib.ext.Order import Order
import sys

# You need to change this to your directory
sys.path.append("Users/Simo/Documents/Interactive-Broker/IbPy")


def error_handler(msg):
    """Handles the capturing of error messages"""
    print "Server Error: %s" % msg

def reply_handler(msg):
    """Handles of server replies"""
    print "Server Response: %s, %s" % (msg.typeName, msg)

def make_contract(symbol, sec_type, exch, prim_exchange, curr):
    """Create a Contract object defining what will
        be purchased, at which exchange and in which currency.
        
        symbol - The ticker symbol for the contract
        sec_type - The security type for the contract ('STK' is 'stock')
        exch - The exchange to carry out the contract on
        prim_exch - The primary exchange to carry out the contract on
        curr - The currency in which to purchase the contract"""
        Contract.m_symbol = symbol
        Contract.m_secType = sec_type
        Contract.m_exchange = exch
        Contract.m_primaryExch = prim_exchange
        Contract.m_currency = curr
        return Contract


def create_order(order_type, quantity, action):
    """Create an Order object (Market/Limit) to go long/short.
        
        order_type - 'MKT', 'LMT' for Market or Limit orders
        quantity - Integral number of assets to order
        action - 'BUY' or 'SELL'"""
    order = Order()
    order.m_orderType = order_type
    order.m_totalQuantity = quantity
    order.m_action = action
    return order


def make_order(action,quantity, price = None):
    
    if price is not None:
        order = Order()
        order.m_orderType = 'LMT'
        order.m_totalQuantity = quantity
        order.m_action = action
        order.m_lmtPrice = price
    else:
        order = Order()
        order.m_orderType = 'MKT'
        order.m_totalQuantity = quantity
        order.m_action = action

    return order


cid = 303

while __name__ == "__main__":
# Connect to the Trader Workstation (TWS) running on the
# usual port of 7496, with a clientId of 999
# (The clientId is chosen by us and we will need
# separate IDs for both the execution connection and
# market data connection)
conn = Connection.create(port=7496, clientId=999)
conn.connect()
    
# Assign the error handling function defined above
# to the TWS connection
conn.register(error_handler, 'Error')
    
# Assign all of the server reply messages to the
# reply_handler function defined above
conn.registerAll(reply_handler)

# Create an order ID which is 'global' for this session. This
# will need incrementing once new orders are submitted.
oid = cid
# Create a contract in Tesla stock via SMART order routing
cont = make_contract('TSLA', 'STK', 'SMART', 'SMART', 'USD')
# Go long 200 shares of Tesla
offer = make_order('BUY', 1, 200)

# Use the connection to the send the order to IB
conn.placeOrder(oid, cont, offer)
# Disconnect from TWS
conn.disconnect()
x = raw_input('enter to resend')
cid += 1
