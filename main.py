from math_functions import study_distribs
from dynamics import generate_init_state, simulate_exchange

import matplotlib.pyplot as plt


'''
(economical) incentive (e.g. earn as much money as possible) triggers actions based on models (e.g. IRL learned patterns (including cognitive biases) and theoretical models) of each EA and input for the models (i.e. observed parameters)
actions limited to buy and sell for market participants. Other EA's are not always that limited, e.g. brokerage houses and market organizers
implement order matching engine with double-sided auction using price-time priority algorithm -https://link.springer.com/chapter/10.1007/978-88-470-1766-5_5 
--> use df.set_index(['price', 'time)]


Specific simplifications: 
- Let us suppose we have two populations, both market participants: value inversors and momentum traders, each associated with a the same incentive: maximize money in 10 years but different model
- Value inversors believe that the market is efficient at start (i.e. each stock is worth what it is worth --> no advantage in buying/selling)

Implement 'microservices architecture'?
Main source of data: OECD.stats
'''

print('Start')

# study_distribs()

[market, investors] = generate_init_state() # companies included in market

# Simulate stock exchange
simulate_exchange(market, investors)

plt.show()

print('End')


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











