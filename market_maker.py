import numpy as np
from asset import Asset
from ea import EA
from math import sqrt


class MarketMaker(EA):
    def __init__(self, shares):
        self.shares = shares
        self.money = 10000 #random between 10000 and 100000 maybe (or normal_dist/x)
        self.greediness = abs(np.random.normal(0, 0.03, 1)[0]) # how undervalued (overvalued) must the stock be to buy (sell) it, has iompact on the spread

    def place_order(self):
        return super().place_order()