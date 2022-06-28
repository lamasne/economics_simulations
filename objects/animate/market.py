import pandas as pd
import numpy as np
import seaborn as sns

from objects.inanimate.order import Order


class Market:
    """
    Entity that links orders
    """

    def __init__(self, companies, name=None, id=None, order_book=None):
        self.id = id if id is not None else name
        self.order_book = order_book if order_book is not None else []
        self.companies = companies

    # Many assumptions here
    def match_bid_ask(self, ticker):
        tol = 0.2  # percent --> 0.2 = 20 cent for 100$ stock

        demands = self.get_demand_for_ticker(ticker)
        supplies = self.get_supply_for_ticker(ticker)

        for demand in demands:
            if supplies:
                min = demand.price
                min_id = 0
                for supply in supplies:
                    if demand.price > supply.price:
                        min_tmp = abs(demand.price - supply.price)
                        if min_tmp < min:
                            min = min_tmp
                            min_id = supply.id

                if min < tol / 100 * demand.price:

                    supply = list(filter(lambda supply: supply.id == min_id, supplies))[
                        0
                    ]

                    price_s = supply.price
                    price_d = demand.price
                    seller = supply.offeror
                    buyer = demand.offeror
                    share = supply.share

                    supplies.remove(
                        supply
                    )  # once investor sold, his ask should be removed

                    seller.sell(share, price_s)
                    buyer.buy(share, price_s)

                    for elem in list(
                        filter(
                            lambda order: order.id == demand.id
                            or order.id == supply.id,
                            self.order_book,
                        )
                    ):
                        self.order_book.remove(elem)
                    # print(f'{buyer} bought {share} from {seller} for {price_s}')

    def process_bid(self, bid, ea, ticker):
        if ea.available_money > bid:
            ea.available_money -= bid
            ea.blocked_money += bid
            self.order_book.append(Order(ticker, "buy", bid, ea, self))

    def process_ask(self, ask, ea, share):
        # relevant_shares = list(filter(lambda share : share.get_ticker() == ticker, ea.available_shares))
        if share:
            ea.available_shares.pop(share.id)
            ea.blocked_shares[share.id] = share
            if not ea.blocked_shares:
                print("ISSUE")
            self.order_book.append(
                Order(share.ticker, "sell", ask, ea, self, share=share)
            )

    def get_buy_price(self, ticker):
        supplies = [order.price for order in self.get_supply_for_ticker(ticker)]
        if supplies:
            return supplies[0]
        else:
            return 0

    def get_sell_price(self, ticker):
        demands = [order.price for order in self.get_supply_for_ticker(ticker)]
        if demands:
            price = demands[0]
        else:
            return 0

    # For bid and ask lists
    def get_demand_for_ticker(self, ticker):
        return list(
            filter(
                lambda order: order.ticker == ticker and order.order_type == "buy",
                self.order_book,
            )
        )

    def get_supply_for_ticker(self, ticker):
        return list(
            filter(
                lambda order: order.ticker == ticker and order.order_type == "sell",
                self.order_book,
            )
        )

    def make_bid_ask_plot(
        self, x_label="price", y_label="quantity", title="Demand and supply curves"
    ):

        demand_pdf = []
        supply_pdf = []
        for order in self.order_book:
            if order.order_type == "buy":
                demand_pdf.append(order.price)
            elif order.order_type == "sell":
                supply_pdf.append(order.price)
            else:
                raise Exception(
                    f"Order type should be either buy or sell, not {order.order_type}"
                )

        # ax.hist(demand_pdf, bins=50, density=True, histtype='stepfilled', alpha=0.2) #bins = nb of separations (rectangles)

        if len(demand_pdf) > 40 and len(supply_pdf) > 40:
            sns.displot([demand_pdf, supply_pdf], kde=True, bins=40)
        elif len(demand_pdf) > 40 and len(supply_pdf) < 40:
            sns.displot(demand_pdf, kde=True, bins=40)
        elif len(supply_pdf) > 40 and len(demand_pdf) < 40:
            sns.displot(supply_pdf, kde=True, bins=40)
