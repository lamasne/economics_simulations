from datetime import datetime
import abc


class Order(metaclass=abc.ABCMeta):
    def __init__(
        self,
        ticker,
        price,
        offeror_fk,
        market_fk,
        time=None,
        id=None,
    ):
        self.ticker = ticker
        self.market_fk = market_fk
        self.price = price
        self.offeror_fk = offeror_fk
        self.time = time if time is not None else datetime.now()
        self.id = (
            id
            if id is not None
            else str(round(self.time.timestamp()))  # resolution: 1[s]
            + "_"
            + str(self.offeror_fk)
            + "_"
            + self.ticker
        )
        # print(f"A new order has been created with id: {self.id}")
