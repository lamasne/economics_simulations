import numpy as np
from ea import EA
from math import sqrt
from scipy.stats import skewnorm


class ValueInversor(EA):
    def __init__(self, shares):
        self.available_shares = shares
        self.blocked_shares = []
        self.available_money = 1000 #random between 10000 and 100000 maybe (or normal_dist/x)
        self.blocked_money=0
        self.accuracy = abs(np.random.normal(0.2, 0.035, 1)[0]) # to estimate impact of news on value. Assumption: cant be less than 5% for human are limited and 20% on average
        self.greediness = abs(np.random.normal(0, 0.03, 1)[0]) # how undervalued (overvalued) must the stock be to buy (sell) it, has iompact on the spread
        self.PE_ratio_of_interest = skewnorm.rvs(a=3, loc=15, scale=3, size=1)[0] # a = asymetry, loc = mu, scale = std

    def sell(self, share, price):
        self.blocked_shares.remove(share)
        self.available_money += price

    def buy(self, share, price):
        self.available_shares.append(share)
        self.blocked_money -= price

    def place_order(self, ticker, news, market):
        share_perceived_value = self.get_perceived_value(ticker, news, market)
        if (self.available_money >  (1+self.greediness)*share_perceived_value):
            self.long(ticker, market, (1-self.greediness)*share_perceived_value)    
        potential_share_to_sell = list(filter(lambda share : share.get_ticker() == ticker, self.available_shares))
        if (potential_share_to_sell):
            self.short(potential_share_to_sell[0], market, (1+self.greediness)*share_perceived_value)

        # if market.get_buy_price(ticker): # if someone interested in selling
        #     share_current_value = market.get_buy_price(ticker)
        #     if share_perceived_value > share_current_value:
        #         self.long(ticker, market, (1-self.greediness)*share_perceived_value)
        #     elif share_perceived_value < share_current_value:
        #         self.short(ticker, market, (1+self.greediness)*share_perceived_value)
        # else:
        #     pass

    def long(self, ticker, market, price):
        market.process_bid(price, self, ticker)
        
    def short(self, share, market, price):
        market.process_ask(price , self, share)

    def get_perceived_value(self, ticker, news_real_impact, market):
        news_estimated_impact = np.random.normal(news_real_impact, sqrt(self.accuracy)/2, 1)[0]
        if market.get_buy_price(ticker):
            return news_estimated_impact * market.get_buy_price(ticker)
        else:
            company = list(filter(lambda company: company.ticker == ticker, market.companies))
            return self.PE_ratio_of_interest*company[0].get_eps()
