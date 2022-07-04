from objects.inanimate.security import Security
from objects.collectionable import Collectionable


class Share(Security, Collectionable):
    def __init__(self, id, ticker, owner_fk=None):
        super().__init__(id)
        self.ticker = ticker
        self.owner_fk = owner_fk if owner_fk is not None else []
