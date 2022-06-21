from objects.inanimate.security import Security


class Share(Security):
    def __init__(self, id, ticker, owner=None):
        super().__init__(id)
        self.ticker = ticker
        self.owner = owner
