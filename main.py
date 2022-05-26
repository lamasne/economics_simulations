import random
import numpy as np
import matplotlib.pyplot as plt
from asset import Asset
from company import Company
from functions import *
from momentum_trader import MomentumTrader
from value_inversor import ValueInversor
from market import Market
import pandas as pd
from math import pi
from parameters import *
from public_news import get_news_real_impact
from alive_progress import alive_bar


# (economical) incentive (e.g. earn as much money as possible) triggers actions based on models (e.g. IRL learned patterns (including cognitive biases) and theoretical models) of each EA and input for the models (i.e. observed parameters)
# actions limited to buy and sell for market participants. Other EA's are not always that limited, e.g. brokerage houses and market organizers
# implement double-sided auction with price-time priority as order matching engine of the market -https://link.springer.com/chapter/10.1007/978-88-470-1766-5_5

# Specific simplifications: 
# - Let us suppose we have two populations, both market participants: value inversors and momentum traders, each associated with a the same incentive: maximize money in 10 years but different model
# - Value inversors believe that the market is efficient at start (i.e. each stock is worth what it is worth --> no advantage in buying/selling)

# Init
company = Company(ticker, annual_profit, nb_shares)
market = Market([company])

undistributed_shares=[]
for i in range(nb_shares):
    undistributed_shares.append(Asset(ticker))

investors=[]
for i in range(nb_investors):
    shares_tmp = []
    nb_shares_tmp = random.randint(0,3)
    if len(undistributed_shares) >= nb_shares_tmp:
        investors.append(ValueInversor(undistributed_shares[0:nb_shares_tmp]))
        for j in range(nb_shares_tmp):
            undistributed_shares.remove(undistributed_shares[0])

for j in range(2):
    news_real_impact = get_news_real_impact(ticker)
    print(f'FLASH NEWS: {news_real_impact}')

    with alive_bar(nb_investors, title='Get orders') as bar:
        for i in get_orders(investors, ticker, news_real_impact, market):
            bar()

    market.make_bid_ask_plot()

    # t = pd.date_range(start=start_time, end='2022-10-13', periods=resolution).to_frame(index=False, name='Time')
    market.match_bid_ask(ticker)
    print(f'Buy price: {market.get_buy_price(ticker)}\nSell price: {market.get_sell_price(ticker)}')

    market.make_bid_ask_plot()

plt.show()
print('end')


# # Momentum trades
# x = np.linspace(0, resolution, resolution)

# prices = start_price*np.ones(100) + np.linspace(0, 7, resolution)
# prices += 10*np.sin(6*pi*x/resolution)
# prices += np.random.normal(0,5,resolution)

# a_trader = MomentumTrader()
# print(f'Money at start {a_trader.money}')

# for idx, elem in enumerate(t['Time']):
#     new_price = prices[idx]
#     if idx != 0:
#         a_stock.update_price(new_price, elem)
#         if idx > 60:
#             is_signal = a_trader.is_momentum_trade(a_stock)
#             if(is_signal != 0):
#                 a_trader.place_order(is_signal, a_stock)

# print(f'Money at the end after selling all shares: {a_trader.money + a_trader.shares.count(a_stock)*a_stock.get_last_price()}')











