import os
import time
import itertools
from numpy import isin
import pandas as pd
from pymongo import MongoClient, UpdateOne
import meta.meta_functions as meta_fcts
from alive_progress import alive_bar
from meta.settings.meta_settings import MONGO_DB_SETTINGS

# singleton to only open connection once
class Dao:
    _instance = None
    _client = None
    _db = None
    # Objects to DB mapping
    col2class = None
    class2col = None

    def __new__(cls):
        """
        Create connection to db in a singleton manner
        """
        if cls._instance is None:
            # Take care of DB-business objects mapping
            import objects.animate.company
            import objects.animate.market
            import objects.inanimate.share
            import objects.animate.value_investor
            import objects.animate.investment_bank
            import objects.inanimate.order_buy
            import objects.inanimate.order_sell

            cls.col2class = {
                "companies": objects.animate.company.Company,
                "markets": objects.animate.market.Market,
                "shares": objects.inanimate.share.Share,
                "investors": objects.animate.value_investor.ValueInvestor,
                "investment_banks": objects.animate.investment_bank.InvestmentBank,
                "orders_buy": objects.inanimate.order_buy.BuyOrder,
                "orders_sell": objects.inanimate.order_sell.SellOrder,
            }
            cls.class2col = {cls.col2class[col]: col for col in cls.col2class.keys()}

            # take care of DB connection settings
            cls._instance = super(Dao, cls).__new__(cls)
            host = MONGO_DB_SETTINGS["host"]
            port = MONGO_DB_SETTINGS["port"]
            try:
                cls._client = MongoClient(host, port)
                print("Created DB interface")
            except:
                raise Exception("Could not connect to MongoDB")

            db_name = MONGO_DB_SETTINGS["db_name"]
            cls._db = cls._client[db_name]

        return cls._instance

    def read_collection(cls, class_to_init, key_id="id", is_fk_obj=False):
        """
        return dict with objects
        """
        objects = {}
        col_name = cls.class2col[class_to_init]
        col_list = cls._db.list_collection_names()
        if col_name not in col_list:
            print(f"Collection: {col_name} does not exist (yet).")
        else:
            # import all data from collection
            collection = cls._db[col_name]
            df = pd.DataFrame(list(collection.find({})))
            df.drop("_id", axis=1, inplace=True)  # axis = 1 for column and not row
            # import foreign keys and make objects (call constructors)
            if is_fk_obj:
                col_to_import = [
                    col for col in df.columns if col.endswith("_fk")
                ]  # necessary for cls.import_foreign_keys
                with alive_bar(
                    len(df.index), title=f"Importing data from {col_name}"
                ) as bar:
                    for row in list(df.to_dict(orient="index").values()):
                        # If there is at least one, import secondary objects using foreign keys
                        if len(col_to_import) > 0:
                            params = cls.import_foreign_keys(row, col_to_import)
                        else:
                            params = row.copy()
                        # print(params)
                        objects[row[key_id]] = class_to_init(**params)
                        bar()
            else:
                for row in list(df.to_dict(orient="index").values()):
                    objects[row[key_id]] = class_to_init(**row)

        return objects

    def update_collection(cls, class_to_init, data, key_id="id"):
        """
        Save objects in database, object-attributes are saved as foreign keys through their id
        params:
        - objects: list of objects
        """
        col_name = cls.class2col[class_to_init]
        if cls._db.drop_collection(cls._db[col_name]):
            print(f"Dropped collection: {col_name}")
        else:
            print(f"Collection: {col_name} does not exist. It will be created.")
        cls.create_objects(col_name, data, key_id=key_id)

    def create_objects(cls, class_to_init, data, key_id="id", is_fk_obj=False):
        """
        Equivalent to create_collection
        """
        col_name = cls.class2col[class_to_init]
        data_df = cls.format_input_data(data)
        cls.validate_data(data_df, key_id)
        if is_fk_obj:
            data_df = cls.make_foreign_keys(data_df)
        formated_data = [row for row in list(data_df.to_dict(orient="index").values())]
        collection = cls._db[col_name]
        collection.insert_many(formated_data)
        # print(f"Inserted {len(data_df.index)} objects in collection: {col_name}")

    def read_objects(cls, class_to_init, id_list, key_id="id", is_fk_obj=False):
        objects = {}
        col_name = cls.class2col[class_to_init]
        col_list = cls._db.list_collection_names()
        if col_name not in col_list:
            print(f"Collection: {col_name} does not exist (yet).")
        else:
            collection = cls._db[col_name]
            df = pd.DataFrame(
                list(collection.find({key_id: {"$in": id_list}}, {"_id": 0}))
            )

            if is_fk_obj:
                col_to_import = [col for col in df.columns if col.endswith("_fk")]
                for row in list(df.to_dict(orient="index").values()):
                    # If there is at least one, import secondary objects using foreign keys
                    params = (
                        row.copy()
                        if len(col_to_import) == 0
                        else cls.import_foreign_keys(row, col_to_import)
                    )
                    objects[row[key_id]] = class_to_init(**params)
            else:
                for row in list(df.to_dict(orient="index").values()):
                    objects[row[key_id]] = class_to_init(**row)

        return objects

    def update_objects(cls, class_to_init, data, key_id="id", is_fk_obj=False):
        """
        updating is about a 100 times slower than inserting, so make sure that's necessary
        inputs:
        - data: either objects --> update all fields, or df/list_of_dict --> update specified fields
        """
        col_name = cls.class2col[class_to_init]
        data_df = cls.format_input_data(data)
        cls.validate_data(data_df, key_id)
        if is_fk_obj:
            data_df = cls.make_foreign_keys(data_df)
        formated_data = [row for row in list(data_df.to_dict(orient="index").values())]
        # print(
        #     f"Updating {len(data_df.index)} objects into collection: {col_name}.\nHave you considered using update_collection()?"
        # )

        # start = time.time()
        cls._db[col_name].bulk_write(
            [
                UpdateOne(
                    {key_id: dto[key_id]},
                    {
                        "$set": dto,
                        # "$setOnInsert": object
                    },
                    upsert=True,
                )
                for dto in formated_data
            ]
        )
        # end = time.time()

        # print(f"Collection: {col_name} updated in {end-start:.2f} seconds")

    def delete_objects(cls, class_to_init, query, key_id="id"):

        # if list of id given, query makes match
        query = query if not isinstance(query, list) else {key_id: {"$in": query}}
        cls._db[cls.class2col[class_to_init]].delete_many(query)

    def find_objects(cls, class_to_init, query, key_id="id"):
        objects = {}
        # if list of id given, query makes match
        query = query if not isinstance(query, list) else {key_id: {"$in": query}}
        col_name = cls.class2col[class_to_init]
        col_list = cls._db.list_collection_names()
        if col_name not in col_list:
            print(f"Collection: {col_name} does not exist (yet).")
        else:
            collection = cls._db[col_name]
            df = pd.DataFrame(list(collection.find(query, {"_id": 0})))
            for row in list(df.to_dict(orient="index").values()):
                objects[row[key_id]] = class_to_init(**row)

        return objects

    def make_foreign_keys(cls, df):
        """Change fields that are objects (to be found in other collections) into list of references through id"""

        for column in df.columns:
            # check if single object
            if not meta_fcts.is_compound(df[column].iloc[0]):
                for att, my_class in itertools.product(
                    df[column], list(cls.col2class.values())
                ):
                    if isinstance(att, my_class):
                        df[column + "_id"] = [att.id for att in df[column]]
                        df.drop(column, axis=1, inplace=True)
                        break
            else:
                # if compound check if values are objects
                for att, my_class in itertools.product(
                    df[column], list(cls.col2class.values())
                ):
                    if any(
                        isinstance(att_att, my_class)
                        for att_att in meta_fcts.get_values_from_compound(att)
                    ):
                        df[column + "_fk"] = [
                            [
                                att_att.id
                                for att_att in meta_fcts.get_values_from_compound(att_2)
                            ]
                            for att_2 in df[column]
                        ]  # assuming keys are the id
                        df.drop(column, axis=1, inplace=True)
                        break

        return df

    def import_foreign_keys(cls, row, col_to_import, is_make_dict=True):
        """
        params:
        - is_make_dict: is the output desired format a dictionnary? Otherwise make list
        """
        params = row.copy()

        # for each attribute-object to import
        for col in col_to_import:
            param_name = col[:-3]  # remove '_id'

            # get collection name and associated class
            if param_name in cls.col2class.keys():
                att_collection_name = param_name
            else:
                for col_name in cls.col2class.keys():
                    if col_name in col:
                        att_collection_name = col_name
                        break
            if att_collection_name is None:
                raise Exception(
                    "The variable name does not contain a valid collection name"
                )
            class_to_import = cls.col2class[att_collection_name]

            # Get foreign key objects
            if meta_fcts.is_compound(row[col]):
                att_cursor = cls._db[att_collection_name].find(
                    {"id": {"$in": [att_id for att_id in row[col]]}}, {"_id": 0}
                )
                if is_make_dict:
                    att_objects = {
                        att_dict["id"]: class_to_import(**att_dict)
                        for att_dict in att_cursor
                    }
                else:
                    att_objects = [
                        class_to_import(**att_dict) for att_dict in att_cursor
                    ]
            else:
                att_cursor = cls._db[att_collection_name].find_one(
                    {"id": row[col]}, {"_id": 0}
                )
                if is_make_dict:
                    att_objects = {
                        att_cursor[0]["id"]: class_to_import(**att_cursor[0])
                    }
                else:
                    att_objects = [class_to_import(**att_cursor[0])]

            del params[col]
            params[param_name] = att_objects

            return params

    def validate_data(cls, data, key_id):
        if any(key_id_value is None for key_id_value in data[key_id]):
            raise Exception(
                f"key_id of data to be inserted into collection must be defined"
            )

    def format_input_data(cls, data):
        """
        if data is a list of objects or single obj, make it a dataframe. If not dataframe, compound of objects, nor single object --> Exception
        """
        # If DataFrame
        if isinstance(data, pd.DataFrame):
            return data

        # If compound of objects
        elif meta_fcts.is_compound(data):
            data_list = meta_fcts.get_values_from_compound(data)
            if any(
                isinstance(data_list[0], my_class)
                for my_class in cls.col2class.values()
            ):
                return pd.DataFrame.from_records([vars(object) for object in data_list])
            # if list of dict
            elif isinstance(data, list):
                return pd.DataFrame.from_records(data)

        # If single object
        elif any(isinstance(data, my_class) for my_class in cls.col2class.values()):
            return pd.DataFrame.from_records([vars(data)])

        raise Exception("Wrong format of objects to be saved")

    def backup_db(cls):
        """copy db_name to /db_dump"""
        os.system(
            "mongodump --db="
            + MONGO_DB_SETTINGS["db_name"]
            + " --out=db_dump"
        )

    def restore_backup(cls):
        """copy db_backup into db_name"""
        settings = MONGO_DB_SETTINGS
        cls._client.drop_database(settings["db_name"])
        print("Dropped database")
        os.system(
            "mongorestore"
            + " --nsFrom "
            + settings["db_name"]
            + ".*"
            + " --nsTo "
            + settings["db_name"]
            + ".*"
            + " db_dump/"
        )

    def drop_db(cls):
        cls._client.drop_database(MONGO_DB_SETTINGS["db_name"])
