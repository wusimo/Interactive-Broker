from pandas.io.data import DataReader
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt

#select the symbol of stock you want to check
symbol = "IBM"
#Select start date
start_date = datetime(2011,12,5)
#Select end date
end_date = datetime(2012,1,1)
#Retrieving the chart
chart = DataReader(symbol,'yahoo',start_date,end_date)

#Using Linear Regression
y = np.array(chart["Close"])
x = np.linspace(1,len(y),num = len(y))

A = np.vstack([x, np.ones(len(x))]).T
m, c = np.linalg.lstsq(A, y)[0]


plt.plot(x, y, 'o', label='Original data', markersize=10)
plt.plot(x, m*x + c, 'r', label='Fitted line')
plt.legend()
plt.show()


#Using the learned coefficient to do the forecast

#print(chart['Adj Close'])