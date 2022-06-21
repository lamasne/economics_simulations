import numpy as np
from objects.animate.investment_bank import InvestmentBank
from objects.animate.company import Company
from objects.animate.market import Market
from objects.animate.value_investor import ValueInvestor
from objects.inanimate.share import Share


mongodb_settings = {"host": "localhost", "port": 27017, "db_name": "econ_simulation"}

# Run params
SCALING_FACTOR = 1e-6
timespan = 2
is_import = True  # if True generate import init state, else generate it
is_from_scratch = True
is_save_init = False

tickers = ["AAPL", "PEAR"]
profit_inits = np.array([1e11, 2e7]) * SCALING_FACTOR  # AAPL annual net income
capital_inits = np.array([2.3e12, 0]) * SCALING_FACTOR
nb_shares_inits = np.array([1.6e10, 0]) * SCALING_FACTOR
# nb_shares_inits = np.array([1.6e10,0],'i') * SCALING_FACTOR       -Python int too large to convert to C long


nb_investors = int(1e9 * SCALING_FACTOR)  # 10 percent of population
nb_traders = int(1e8 * SCALING_FACTOR)  # 1 percent of population

col2class = {
    "companies": Company,
    "shares": Share,
    "markets": Market,
    "inverstors": ValueInvestor,
    "investment_banks": InvestmentBank,
}
