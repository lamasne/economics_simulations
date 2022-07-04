import numpy as np
from ea import EA
from math import sqrt


class MarketMaker(EA):
    def __init__(self, shares_fk):
        self.shares_fk = shares_fk
        self.money = 10000  # random between 10000 and 100000 maybe (or normal_dist/x)
        self.greediness = abs(
            np.random.normal(0, 0.03, 1)[0]
        )  # how undervalued (overvalued) must the stock be to buy (sell) it, has iompact on the spread

    def place_order(self):
        return super().place_order()
