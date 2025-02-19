import pandas as pd
import seaborn as sns
import objects.animate.value_investor  # Should only be market participant + do not import class because of circular dependency
import objects.animate.market_participant
from objects.inanimate.order_buy import BuyOrder
from objects.inanimate.order_sell import SellOrder
from objects.inanimate.share import Share
from objects.collectionable import Collectionable
from dao_pymongo.dao import Dao
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
        # for now one share by transaction (and order)
        demands = market_repo.MarketRepo().query_ordered_demand(ticker, self.id)
        supplies = market_repo.MarketRepo().query_ordered_supply(ticker, self.id)
        transactions = []
        for idx, demand in enumerate(demands):  # already ordered in (time 1, price 2)
            # get contemporary supply to correct match-making latency
            contemp_supply = [row for row in supplies if row["time"] <= demand["time"]]
            if len(contemp_supply) > 0:
                supply = contemp_supply[
                    0
                ]  # first as it is already ordered (price 1, time 2)
                price = supply["price"]
                if price <= demand["price"]:
                    # Share changes of owner, and money is changed too
                    transactions.append(
                        {
                            "seller_fk": supply["offeror_fk"],
                            "buyer_fk": demand["offeror_fk"],
                            "share_fk": supply["share_fk"],
                            "price": price,
                            "buy_order_fk": demand["id"],
                            "sell_order_fk": supply["id"],
                        }
                    )
                    # Orders must removed as it is not updated from table in the loop
                    supplies.remove(supply)

        if len(transactions) > 0:
            self.make_transactions(pd.DataFrame.from_records(transactions))

    def make_transactions(self, data):
        dao = Dao()
        # Import pojos

        # print(data.to_string())

        sellers = dao.read_objects(
            objects.animate.value_investor.ValueInvestor, data["seller_fk"].tolist()
        )
        buyers = dao.read_objects(
            objects.animate.value_investor.ValueInvestor, data["buyer_fk"].tolist()
        )
        shares = dao.read_objects(Share, data["share_fk"].tolist())

        # Iterate over transactions
        for row in list(data.to_dict(orient="index").values()):
            seller = sellers[row["seller_fk"]]
            buyer = buyers[row["buyer_fk"]]
            share = shares[row["share_fk"]]
            price = row["price"]

            if self.validate_transaction(seller, buyer, share, price):
                seller.exchange_money(price)
                buyer.blocked_money -= price
                share.update_owner(row["buyer_fk"])
                share.update_availability(True)
            else:
                print("Transaction cancelled")

        dao.delete_objects(BuyOrder, data["buy_order_fk"].tolist())
        dao.delete_objects(SellOrder, data["sell_order_fk"].tolist())

    # def make_transaction(
    #     self, seller_fk, buyer_fk, share_fk, price, buy_order_fk, sell_order_fk
    # ):
    #     """
    #     for now one share by transaction
    #     """
    #     dao = Dao()
    #     seller = list(
    #         dao.read_objects(
    #             objects.animate.value_investor.ValueInvestor,
    #             [seller_fk],
    #         ).values()
    #     )[0]
    #     buyer = list(
    #         dao.read_objects(
    #             objects.animate.value_investor.ValueInvestor,
    #             [buyer_fk],
    #         ).values()
    #     )[0]
    #     share = list(
    #         dao.read_objects(
    #             Share,
    #             [share_fk],
    #         ).values()
    #     )[0]
    #     self.validate_transaction(seller, buyer, share)
    #     seller.exchange_money(price)
    #     buyer.exchange_money(-price)
    #     share.update_owner(buyer_fk)

    #     dao.delete_objects(BuyOrder, [buy_order_fk])
    #     dao.delete_objects(SellOrder, [sell_order_fk])

    #     # print(f'{buyer} bought {share} from {seller} for {price_s}')

    def validate_transaction(self, seller, buyer, share, price):
        conditions = []
        conditions.append(buyer.blocked_money >= price)
        conditions.append(share.availability == False)  # THIS SHOULD NOT BE HERE
        conditions.append(share.owner_fk == seller.id)
        return True if all(conditions) else False

    def process_bid(self, bid, ea_id, ticker):
        ea = Dao().find_objects(objects.animate.value_investor.ValueInvestor, [ea_id])[
            ea_id
        ]
        if ea.available_money > bid:
            # Should produce an event instead of modifying object
            ea.available_money -= bid
            ea.blocked_money += bid
            ea.save()
            new_order = BuyOrder(ticker, bid, ea.id, self.id)
            Dao().create_objects(BuyOrder, new_order)
        else:
            print("Buy order rejected for lack of funds")

    def process_ask(self, ask, ea_id, share_id):
        # relevant_shares = list(filter(lambda share : share.get_ticker() == ticker, ea.available_shares))
        share = Dao().find_objects(Share, [share_id])[share_id]
        if share:
            if share.availability:
                # Block share
                market_repo.MarketRepo().freeze_shares([share.id])
                # Create sell order
                new_order = SellOrder(
                    share.ticker, ask, ea_id, self.id, share_fk=share.id
                )
                Dao().create_objects(SellOrder, new_order)
            else:
                print(
                    "Sell order rejected because one already exists for that share. Cancel the previous order first."
                )

    def get_buy_price(self, ticker):
        supplies = market_repo.MarketRepo().query_ordered_supply(ticker, self.id)
        if supplies:
            return supplies[0]["price"]
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
