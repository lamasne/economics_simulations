import pandas as pd
import numpy as np
import seaborn as sns
import objects.animate.value_investor  # Do not import class because of circular dependency
from objects.inanimate.order_buy import BuyOrder
from objects.inanimate.order_sell import SellOrder
from objects.inanimate.share import Share
from objects.collectionable import Collectionable
from db_interface.dao_MongoDB import Dao
import model_settings as model_settings
import db_interface.market_repo as market_repo


class Market(Collectionable):
    """
    Entity that links orders
    """

    def __init__(self, companies_fk, name=None, id=None):
        self.id = id if id is not None else name
        self.companies_fk = companies_fk

    # Many assumptions here
    def match_bid_ask(self, ticker):
        tol = 0.2  # percent --> 0.2 = 20 cent for 100$ stock

        # demands = self.get_demand_for_ticker(ticker)
        # supplies = self.get_supply_for_ticker(ticker)

        demands = market_repo.MarketRepo().query_ordered_demand(ticker, self.id)
        supplies = market_repo.MarketRepo().query_ordered_supply(ticker, self.id)
        dao = Dao()
        for demand in demands:
            # get contemporary supply to correct match-making latency
            contemp_supply = [row for row in supplies if row["time"] <= demand["time"]]
            if len(contemp_supply) > 0:
                supply = contemp_supply[0]  # first as it is already ordered
                price_s = supply["price"]
                if price_s <= demand["price"]:
                    seller = list(
                        dao.read_objects(
                            objects.animate.value_investor.ValueInvestor,
                            [supply["offeror_fk"]],
                        ).values()
                    )[0]
                    buyer = list(
                        dao.read_objects(
                            objects.animate.value_investor.ValueInvestor,
                            [demand["offeror_fk"]],
                        ).values()
                    )[0]

                    # Share changes of owner, and money is changed too
                    seller.sell(supply["share_fk"], price_s)
                    buyer.buy(supply["share_fk"], price_s)

                    # Orders are removed
                    supplies.remove(supply)  # for the loop
                    dao.delete_objects(BuyOrder, [demand["id"]])
                    dao.delete_objects(SellOrder, [supply["id"]])

                    # print(f'{buyer} bought {share} from {seller} for {price_s}')

        # self.save()

    def process_bid(self, bid, ea, ticker):
        if ea.available_money > bid:
            ea.available_money -= bid
            ea.blocked_money += bid
            new_order = BuyOrder(ticker, bid, ea.id, self.id)
            # Next line should somehow be in class Order and save() fct should be inherited for all objects (maybe) or maybe just save should be in respective class
            Dao().create_objects(BuyOrder, new_order)
            self.save()

    def process_ask(self, ask, ea, share):
        # relevant_shares = list(filter(lambda share : share.get_ticker() == ticker, ea.available_shares))
        if share:
            ea.available_shares_fk.remove(share.id)
            ea.blocked_shares_fk.append(share.id)
            if not ea.blocked_shares_fk:
                print("ISSUE with order management")
            new_order = SellOrder(share.ticker, ask, ea.id, self.id, share_fk=share.id)
            Dao().create_objects(SellOrder, new_order)
            self.save()

    def get_buy_price(self, ticker):
        supplies = [order.price for order in self.get_supply_for_ticker(ticker)]
        if supplies:
            return supplies[0]
        else:
            return 0

    def get_sell_price(self, ticker):
        demands = [order.price for order in self.get_demand_for_ticker(ticker)]
        if demands:
            return demands[0]
        else:
            return 0

    # For bid and ask lists
    def get_demand_for_ticker(self, ticker):
        """return list of 'buy' orders for given ticker"""
        return list(
            filter(
                lambda order: order.ticker == ticker,
                self.get_order_book()["demand"],
            )
        )

    def get_supply_for_ticker(self, ticker):
        """return list of 'sell' orders for given ticker"""
        return list(
            filter(
                lambda order: order.ticker == ticker,
                self.get_order_book()["supply"],
            )
        )

    def make_bid_ask_plot(
        self, x_label="price", y_label="quantity", title="Demand and supply curves"
    ):

        order_book = self.get_order_book()
        demand_pdf = [order.price for order in order_book["demand"]]
        supply_pdf = [order.price for order in order_book["supply"]]

        # ax.hist(demand_pdf, bins=50, density=True, histtype='stepfilled', alpha=0.2) #bins = nb of separations (rectangles)

        if len(demand_pdf) > 40 and len(supply_pdf) > 40:
            sns.displot([demand_pdf, supply_pdf], kde=True, bins=40)
        elif len(demand_pdf) > 40 and len(supply_pdf) < 40:
            sns.displot(demand_pdf, kde=True, bins=40)
        elif len(supply_pdf) > 40 and len(demand_pdf) < 40:
            sns.displot(supply_pdf, kde=True, bins=40)

    def get_order_book(self, is_dict=False):
        dao = Dao()
        demand = dao.find_objects(BuyOrder, {"market_fk": self.id})
        supply = dao.find_objects(SellOrder, {"market_fk": self.id})
        if not is_dict:
            demand = list(demand.values())
            supply = list(supply.values())
        return {"demand": demand, "supply": supply}
