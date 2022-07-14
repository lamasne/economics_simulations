from db_interface.dao_MongoDB import Dao
import objects.animate.value_investor
import objects.inanimate.share
import numpy as np


class InvestorRepo:
    def get_shares(cls, inv_id):
        dao = Dao()
        col_name = dao.class2col[objects.inanimate.share.Share]
        collection = dao._db[col_name]
        result = list(
            collection.find(
                {"owner_fk": int(inv_id)},
                {"_id": 0},
            )
        )
        result = [objects.inanimate.share.Share(**data) for data in result]
        return result

    def get_richest_investors(cls):
        """
        return top 5 richest investors
        """
        dao = Dao()
        col_name = dao.class2col[objects.animate.value_investor.ValueInvestor]
        collection = dao._db[col_name]
        inversors_DTO = list(
            collection.find({}, {"_id": 0, "id": 1, "available_money": 1})
        )
        money_threshold_top_5 = np.percentile(
            [investor["available_money"] for investor in inversors_DTO], 95
        )
        print(
            f"money threshold to be part of the top 5 investors: {money_threshold_top_5}"
        )
        # filtered = list(
        #     filter(
        #         lambda investor: investor['available_money'] >= money_threshold_top_5,
        #         inversors_DTO,
        #     )
        # )
        # result = [inv['id'] for inv in filtered]
        result = list(
            collection.find(
                {"available_money": {"$gt": money_threshold_top_5}},
                {
                    "_id": 0,
                    # "id": 1,
                },
            )
        )

        result = [
            objects.animate.value_investor.ValueInvestor(**data) for data in result
        ]
        return result
