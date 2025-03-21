from objects.animate.market_participant import MarketParticipant
from objects.collectionable import Collectionable
from dao_pymongo.dao import Dao
import meta.settings.model_settings as model_settings


class Company(Collectionable, MarketParticipant):
    def __init__(self, ticker, profit, market_cap, nb_of_shares, capital, id=None):
        self.ticker = ticker
        self.id = id if id is not None else ticker
        self.profit = profit  # $ per year
        self.market_cap = market_cap
        self.capital = capital  # i.e. cash
        # nb of shares issued during IPO + subsequent share dilutions
        self.nb_of_shares = nb_of_shares

    def get_eps(self):
        return self.profit / self.nb_of_shares

    def get_PE(self):
        return self.market_cap / self.profit

    def change_market_cap(self, amount):
        self.market_cap += amount
        self.save()

    def set_nb_shares(self, nb_shares):
        self.nb_of_shares = nb_shares
        self.save()

    def exchange_money(self, price):
        self.capital += price
        self.save()

    def place_buy_limit_order(self, ticker, market, price):
        super().place_buy_limit_order(ticker, market, price)

    def place_sell_limit_order(self, share, market, price):
        super().place_sell_limit_order(share, market, price)
