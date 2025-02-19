from math import floor
from scipy import stats

import meta.settings.model_settings as model_settings
from objects.collectionable import Collectionable

# should implement EA or company maybe?
class InvestmentBank(Collectionable):
    def __init__(self, id, cash, shares_fk=None):
        self.id = id
        self.shares_fk = shares_fk if shares_fk is not None else []
        self.cash = cash  # random between 10000 and 100000 maybe (or normal_dist/x)

    def evaluate_company(self, company):
        # for now I assume all invest. banks follow the same methodology, and all companies sell at around the same Price to Earning ratio (defined in parameters) with a random variation
        idx_similar_company = 0
        typical_PE = (
            model_settings.market_cap_inits[idx_similar_company]
            / model_settings.profit_inits[idx_similar_company]
        )  # should depend on sector
        estimated_PE = stats.norm.rvs(typical_PE, scale=3, size=1)[
            idx_similar_company
        ]  # similar
        potential_market_cap = estimated_PE * company.profit
        typical_price = (
            model_settings.market_cap_inits[idx_similar_company]
            / model_settings.nb_shares_inits[idx_similar_company]
        )
        potential_nb_shares = floor(potential_market_cap / typical_price)

        return [potential_market_cap, potential_nb_shares]
