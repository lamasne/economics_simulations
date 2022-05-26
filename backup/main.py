import numpy as np
import matplotlib.pyplot as plt
from asset import Asset
from functions import *
from momentum_trader import MomentumTrader
from value_inversor import ValueInversor
from market import Market
import pandas as pd
from math import pi
from parameters import *
from public_news import get_news_real_impact

# (economical) incentive (e.g. earn as much money as possible) triggers actions based on models (e.g. IRL learned patterns (including cognitive biases) and theoretical models) of each EA and input for the models (i.e. observed parameters)
# actions limited to buy and sell for market participants. Other EA's are not always that limited, e.g. brokerage houses and market organizers

# Specific simplifications: 
# - Let us suppose we have two populations, both market participants: value inversors and momentum traders, each associated with a the same incentive: maximize money in 10 years but different model
# - Value inversors believe that the market is efficient at start (i.e. each stock is worth what it is worth --> no advantage in buying/selling)

# Init
a_stock = Asset('AAPL', start_time, start_price)
t = pd.date_range(start=start_time, end='2022-10-13', periods=resolution).to_frame(index=False, name='Time')
market = Market()

# Value inversors
an_inversor = ValueInversor()

x0 = start_price - 5
x1 = start_price + 5
x = np.linspace(x0,x1,resolution)

news_real_impact = get_news_real_impact(a_stock)
an_inversor.place_order(a_stock, news_real_impact, market)
market.match_bid_ask()

#  



# Momentum trades
x = np.linspace(0, resolution, resolution)

prices = start_price*np.ones(100) + np.linspace(0, 7, resolution)
prices += 10*np.sin(6*pi*x/resolution)
prices += np.random.normal(0,5,resolution)

a_trader = MomentumTrader()
print(f'Money at start {a_trader.money}')

for idx, elem in enumerate(t['Time']):
    new_price = prices[idx]
    if idx != 0:
        a_stock.update_price(new_price, elem)
        if idx > 60:
            is_signal = a_trader.is_momentum_trade(a_stock)
            if(is_signal != 0):
                a_trader.place_order(is_signal, a_stock)

print(f'Money at the end after selling all shares: {a_trader.money + a_trader.shares.count(a_stock)*a_stock.get_last_price()}')






plt.show()





