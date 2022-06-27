from datetime import datetime


class Order:
    def __init__(self, ticker, type, price, offeror, market, id=None):
        self.ticker = ticker
        self.market = market
        self.type = type  # bid or ask
        self.price = price
        self.offeror = offeror
        self.time = datetime.now()
        self.id = (
            id if id is not None else self.time + "_" + self.offeror + "_" + self.ticker
        )
