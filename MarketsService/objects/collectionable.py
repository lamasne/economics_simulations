from dao_pymongo.dao import Dao


class Collectionable:
    def save(self):
        return Dao().update_objects(self.__class__, self)
