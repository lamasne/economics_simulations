import numpy as np
from scipy import stats
import time

import pymongo
import os
import matplotlib.pyplot as plt
import meta.settings.model_settings as model_settings
from meta.settings.meta_settings import outputs_folder

# import unitary_tests as unit_test
from dynamics.main_fcts import generate_init_state, simulate_exchange
from testing.math_functions import study_distribs
import meta.meta_functions as meta_fcts

"""
Documentation in folder ./documentation

To do:
- implement order matching engine with double-sided auction using price-time priority algorithm -https://link.springer.com/chapter/10.1007/978-88-470-1766-5_5 
--> make it run in parallel with the investors' simulation by using 'multiprocess'

- the blocked_shares, available_shares should be properties of share, not valueInvestor and be blocked by market, not investor

- Main source of data: OECD.stats
"""


print("\n----------------------------\nStart\n----------------------------")

# # Tests
# res = unit_test.test_make_IPO()
# study_distribs()

# Simulate stock exchange
simulate_exchange()

# Print into pdf
try:
    meta_fcts.multipage(os.path.join(outputs_folder, "multipage.pdf"))
except:
    # if running from containers, copy to local machine
    path_in_container = os.path.join(os.getcwd(), "multipage.pdf")
    meta_fcts.multipage(path_in_container)
    # docker.cp(path_in_container, outputs_folder)
    print("go")
    time.sleep(120)
plt.show()

print("End")


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
