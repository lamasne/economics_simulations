from db_interface.dao_MongoDB import Dao
import objects.inanimate.order_buy
import objects.inanimate.order_sell
import objects.inanimate.share
import objects.animate.market
import pymongo
import pandas as pd


class MarketRepo:
    def freeze_shares(cls, share_ids):
        share_dto = [{"id": share_id, "availability": False} for share_id in share_ids]
        Dao().update_objects(objects.inanimate.share.Share, share_dto)

    def create_index_match_making(cls):
        dao = Dao()
        dao._db[dao.class2col[objects.inanimate.order_sell.SellOrder]].create_index(
            [("price", pymongo.ASCENDING), ("time", pymongo.ASCENDING)]
        )
        dao._db[dao.class2col[objects.inanimate.order_buy.BuyOrder]].create_index(
            [("time", pymongo.ASCENDING)]
        )
        # Dao()._db[globals.class2col(Market)].createIndex({"price": 1, "time": 1})

    def query_ordered_demand(cls, ticker, market_fk):
        dao = Dao()
        col_name = dao.class2col[objects.inanimate.order_buy.BuyOrder]

        col_list = dao._db.list_collection_names()
        if col_name not in col_list:
            raise Exception(f"Collection: {col_name} does not exist (yet).")

        else:
            collection = dao._db[col_name]
            df = pd.DataFrame(
                list(
                    collection.find(
                        {"ticker": ticker, "market_fk": market_fk},
                        {"_id": 0},
                    ).sort("time", 1)
                )
            )
            return list(df.to_dict(orient="index").values())

    def query_ordered_supply(cls, ticker, market_fk):
        dao = Dao()
        col_name = dao.class2col[objects.inanimate.order_sell.SellOrder]

        col_list = dao._db.list_collection_names()
        if col_name not in col_list:
            raise Exception(f"Collection: {col_name} does not exist (yet).")

        else:
            collection = dao._db[col_name]
            df = pd.DataFrame(
                list(
                    collection.find(
                        {"ticker": ticker, "market_fk": market_fk},
                        {"_id": 0},
                    ).sort([("price", pymongo.ASCENDING), ("time", pymongo.ASCENDING)])
                )
            )
            return list(df.to_dict(orient="index").values())
