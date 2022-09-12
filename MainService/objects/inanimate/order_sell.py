from objects.inanimate.order import Order
from objects.collectionable import Collectionable


class SellOrder(Order, Collectionable):
    def __init__(
        self,
        ticker,
        price,
        offeror_fk,
        market_fk,
        share_fk,
        time=None,
        id=None,
    ):
        super().__init__(
            ticker,
            price,
            offeror_fk,
            market_fk,
            time=None,
            id=None,
        )
        self.share_fk = share_fk
