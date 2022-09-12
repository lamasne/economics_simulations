from objects.inanimate.security import Security
from objects.collectionable import Collectionable


class Share(Security, Collectionable):
    def __init__(self, id, ticker, availability=True, owner_fk=None):
        super().__init__(id)
        self.ticker = ticker
        self.availability = availability
        self.owner_fk = owner_fk if owner_fk is not None else []

    def update_owner(self, new_owner_fk):
        self.owner_fk = new_owner_fk
        self.save()

    def update_availability(self, availability):
        self.availability = availability
        self.save()
