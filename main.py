import matplotlib.pyplot as plt
import meta.globals as globals
from meta.repository import DB_interface
import unitary_tests as unit_test
from dynamics.main_fcts import generate_init_state, simulate_exchange
from meta.math_functions import study_distribs

"""
Documentation in folder ./documentation

To do:
- implement order matching engine with double-sided auction using price-time priority algorithm -https://link.springer.com/chapter/10.1007/978-88-470-1766-5_5 
--> use df.set_index(['price', 'time)]

- Implement 'microservices architecture'?

- Main source of data: OECD.stats
"""


print("\n----------------------------\nStart\n----------------------------")


# # Tests
# unit_test.test_insert_df()
# study_distribs()


[companies, shares, markets, investors, inv_banks] = generate_init_state(
    globals.is_import, globals.is_from_scratch, globals.is_save_init
)

# Simulate stock exchange
simulate_exchange(markets["Nasdaq"], list(investors.values()), list(inv_banks.values()))

try:
    DB_interface(None)._client.close()
except:
    print("No connection to close")

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
