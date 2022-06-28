from datetime import datetime


class Order:
    def __init__(self, ticker, order_type, price, offeror, market, share=None, id=None):
        self.ticker = ticker
        self.market = market
        self.order_type = order_type  # bid=buy or ask=sell
        self.price = price
        self.offeror = offeror
        self.time = datetime.now()
        self.share = share
        self.id = (
            id
            if id is not None
            else str(round(self.time.timestamp()))  # resolution: 1[s]
            + "_"
            + str(self.offeror.id)
            + "_"
            + self.ticker
        )
        # print(f"A new order has been created with id: {self.id}")
