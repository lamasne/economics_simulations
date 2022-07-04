import numpy as np

# Run params
SCALING_FACTOR = 1e-7
timespan = 2
is_import = False  # if True generate import init state, else generate it


tickers = ["AAPL", "PEAR"]
profit_inits = np.array([1e11, 2e8]) * SCALING_FACTOR  # AAPL annual net income
market_cap_inits = np.array([2.3e12, 0]) * SCALING_FACTOR
nb_shares_inits = np.array([1.6e10, 0]) * SCALING_FACTOR
# nb_shares_inits = np.array([1.6e10,0],'i') * SCALING_FACTOR       -Python int too large to convert to C long


nb_investors = int(1e9 * SCALING_FACTOR)  # 10 percent of population
nb_traders = int(1e8 * SCALING_FACTOR)  # 1 percent of population
