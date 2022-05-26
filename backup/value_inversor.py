import numpy as np
from ea import EA
from math import sqrt


class ValueInversor(EA):
    def __init__(self):
        self.shares = []
        self.money = 1000 #random between 10000 and 100000 maybe (or normal_dist/x)
        self.accuracy = abs(np.random.normal(0.2, 0.035, 1)[0]) # to estimate impact of news on value. Assumption: cant be less than 5% for human are limited and 20% on average
        self.greediness = abs(np.random.normal(0, 0.03, 1)[0]) # how undervalued (overvalued) must the stock be to buy (sell) it, has iompact on the spread

    def sell(self, share, price):
        self.shares.remove(share)
        self.money += price

    def buy(self, share, price):
        self.shares.append(share)
        self.money -= price

    def place_order(self, share, news, market):
        share_perceived_value = self.get_perceived_value(share, news)
        share_current_value = share.get_last_price()
        if share_perceived_value > share_current_value:
            market.append_bid((1+self.greediness)*share_current_value, self)
        elif share_perceived_value < share_current_value:
            market.append_ask((1-self.greediness)*share_current_value , self)

    def get_perceived_value(self, share, news_real_impact):
        news_estimated_impact = np.random.normal(news_real_impact, sqrt(self.accuracy)/2, 1)[0]
        return news_estimated_impact * share.get_last_price()

