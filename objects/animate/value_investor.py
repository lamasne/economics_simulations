from unittest import expectedFailure
import numpy as np
from objects.animate.company import Company
import objects.animate.market  # Do not import class because of circular dependency
from objects.inanimate.share import Share
from objects.collectionable import Collectionable
from db_interface.dao_MongoDB import Dao
from objects.animate.ea import EA
import model_settings as model_settings
from math import sqrt
from scipy.stats import skewnorm


class ValueInvestor(EA, Collectionable):
    def __init__(
        self,
        available_money,
        blocked_money=None,
        id=None,
        available_shares_fk=None,
        blocked_shares_fk=None,
        accuracy=None,
        greediness=None,
    ):  # dont do shares_fk = [], it makes it the same default object for all instances -- https://stackoverflow.com/questions/4841782/python-constructor-and-default-value
        self.available_money = (
            available_money  # random between 10000 and 100000 maybe (or normal_dist/x)
        )
        self.blocked_money = blocked_money if blocked_money is not None else 0
        self.available_shares_fk = (
            available_shares_fk if available_shares_fk is not None else []
        )
        self.blocked_shares_fk = (
            blocked_shares_fk if blocked_shares_fk is not None else []
        )
        self.id = id
        self.accuracy = (
            accuracy
            if accuracy is not None
            else 0.05 + abs(np.random.normal(0.15, 0.25, 1)[0])
        )  # to estimate impact of news on value. Assumption: cant be less than 5% for human are limited and 20% on average
        self.greediness = 0
        # self.greediness = (
        #     greediness
        #     if greediness is not None
        #     else abs(np.random.normal(0, 0.03, 1)[0])
        # )  # how undervalued (overvalued) must the stock be to buy (sell) it, has impact on the spread

    def react_to_news(self, news):
        """
        main activities of the class
        """
        ticker = news["ticker"]
        market = Dao().read_objects(objects.animate.market.Market, [news["market_id"]])[
            news["market_id"]
        ]
        share_perceived_value = self.get_perceived_value(news)
        if self.available_money > (1 + self.greediness) * share_perceived_value:
            self.long(ticker, market, (1 - self.greediness) * share_perceived_value)

        available_shares = Dao().read_objects(Share, self.available_shares_fk)
        potential_share_to_sell = list(
            filter(lambda share: share.ticker == ticker, available_shares.values())
        )
        if potential_share_to_sell:
            self.short(
                potential_share_to_sell[0],
                market,
                (1 + self.greediness) * share_perceived_value,
            )

        # if market.get_buy_price(ticker): # if someone interested in selling
        #     share_current_value = market.get_buy_price(ticker)
        #     if share_perceived_value > share_current_value:
        #         self.long(ticker, market, (1-self.greediness)*share_perceived_value)
        #     elif share_perceived_value < share_current_value:
        #         self.short(ticker, market, (1+self.greediness)*share_perceived_value)
        # else:
        #     pass

    def sell(self, share_fk, price, through_3rd_party=True):
        if through_3rd_party:
            self.blocked_shares_fk.remove(share_fk)
        else:
            self.available_shares_fk.remove(share_fk)
        self.available_money += price
        self.save()

    def buy(self, share_fk, price, through_3rd_party=True):
        if through_3rd_party:
            if self.check_ability_to_pay(price, self.blocked_money):
                self.blocked_money -= price
                self.available_shares_fk.append(share_fk)
                self.save()
                return 1
            else:
                return 0
        else:
            if self.check_ability_to_pay(price, self.available_money):
                self.available_money -= price
                self.available_shares_fk.append(share_fk)
                self.save()
                return 1
            else:
                return 0

    def check_ability_to_pay(self, price, money):
        return False if price > money else True

    def long(self, ticker, market, price):
        market.process_bid(price, self, ticker)
        self.save()

    def short(self, share, market, price):
        market.process_ask(price, self, share)
        self.save()

    def get_perceived_value(self, news):
        ticker = news["ticker"]
        market = Dao().read_objects(objects.animate.market.Market, [news["market_id"]])[
            news["market_id"]
        ]
        news_estimated_impact = np.random.normal(
            news["impact"], sqrt(self.accuracy) / 2, 1
        )[0]
        # if market.get_buy_price(ticker):
        #     return news_estimated_impact * market.get_buy_price(ticker)
        # else:
        company = Dao().read_objects(Company, [ticker])[ticker]
        new_eps = (
            company.get_eps() * news_estimated_impact
        )  # Assuming the news_impact multiplies the future profit
        return self.compute_PE_of_interest(0) * new_eps

    def compute_PE_of_interest(self, company_type):
        """
        Still to be implemented correctly, e.g. should depend on sector
        """
        typical_PE = (
            model_settings.market_cap_inits[company_type]
            / model_settings.profit_inits[company_type]
        )
        PE_ratio_of_interest = skewnorm.rvs(a=3, loc=typical_PE, scale=3, size=1)[
            0
        ]  # a = asymetry, loc = mu, scale = std

        return PE_ratio_of_interest
