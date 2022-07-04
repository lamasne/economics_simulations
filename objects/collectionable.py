from db_interface.dao_MongoDB import Dao


class Collectionable:
    def save(self):
        return Dao().update_objects(self.__class__, self)
