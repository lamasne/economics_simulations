from math import floor
from scipy import stats

import meta.globals as globals

# should implement EA or company maybe?
class InvestmentBank:
    def __init__(self, id, cash, shares):
        self.id = id
        self.shares = shares
        self.cash = cash  # random between 10000 and 100000 maybe (or normal_dist/x)

    def evaluate_company(self, company):
        # for now I assume all invest. banks follow the same methodology, and all companies sell at around the same Price to Earning ratio (defined in parameters) with a random variation
        idx_similar_company = 0
        typical_PE = (
            globals.capital_inits[idx_similar_company]
            / globals.profit_inits[idx_similar_company]
        )  # should depend on sector
        estimated_PE = stats.norm.rvs(typical_PE, scale=3, size=1)[
            idx_similar_company
        ]  # similar
        potential_capital = estimated_PE * company.profit
        typical_price = (
            globals.capital_inits[idx_similar_company]
            / globals.nb_shares_inits[idx_similar_company]
        )
        potential_nb_shares = floor(potential_capital / typical_price)

        return [potential_capital, potential_nb_shares]
