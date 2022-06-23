from http import client
import itertools
import numpy as np
import pandas as pd
from pymongo import MongoClient, ReplaceOne
import pymongo
from objects.animate.value_investor import ValueInvestor
import meta.globals as globals
import json
import meta.meta_functions as meta_fcts
from alive_progress import alive_bar


# singleton to only open connection once
class DB_interface:
    _instance = None
    _client = None
    _db = None

    def __new__(cls, mongodb_settings):
        if cls._instance is None:
            cls._instance = super(DB_interface, cls).__new__(cls)
            host = mongodb_settings["host"]
            port = mongodb_settings["port"]
            try:
                cls._client = MongoClient(host, port)
                print("Created DB interface")
            except:
                raise Exception("Could not connect to MongoDB")

            db_name = mongodb_settings["db_name"]
            cls._db = cls._client[db_name]

            return cls._instance

    def create_collection_from_objects(
        cls, col_name, objects, is_from_scratch=False, key_id="id"
    ):
        """
        Prepare init state of collection in database.
        params:
        - objects: list of objects
        - is_from_scratch: if True, only insert new data, else will keep previous records as part of the new state
        """
        col_list = cls._db.list_collection_names()

        if col_name not in col_list:
            print(f"Collection: {col_name} does not exist. It will be created")
        elif is_from_scratch:
            cls.reset_collection(col_name)
        cls.save_objects(col_name, objects, key_id=key_id)

    def create_collection_from_df(
        cls,
        col_name,
        data,
        is_from_scratch=False,
        key_id="id",
    ):
        """
        Prepare init state of collection in database.
        params:
        - is_from_scratch: if True, only insert new data, else will keep previous records as part of the new state
        """
        col_list = cls._db.list_collection_names()

        if col_name not in col_list:
            print(f"Collection: {col_name} does not exist. It will be created")
        elif is_from_scratch:
            cls.reset_collection(col_name)
        cls.insert_df(col_name, data, upsert=True, key_id=key_id)

    def reset_collection(cls, collection_name):
        collection = cls._db[collection_name]

        if collection.delete_many({}):
            print(f"Deleted all records from collection: {collection_name}")
        else:
            print(f"Could not delete records from collection: {collection_name}")

    def save_objects(cls, collection_name, objects, key_id):
        collection = cls._db[collection_name]

        df = pd.DataFrame.from_records(
            [vars(objects[object_key]) for object_key in objects.keys()]
        )
        df = cls.make_foreign_keys(df)

        if any(key_id_value is None for key_id_value in df[key_id]):
            raise Exception(
                f"key_id of data to be inserted into collection: '{collection_name}' must be defined"
            )

        else:
            formated_data = [row for row in list(df.to_dict(orient="index").values())]
            with alive_bar(
                len(formated_data), title=f"Saving data in {collection_name}"
            ) as bar:
                for object in formated_data:
                    collection.replace_one({"id": object[key_id]}, object, upsert=True)
                    bar()

            print(
                f"Finished {len(formated_data)} updates/insertions into collection: {collection_name}"
            )

    def load_objects_from_db(cls, col_name):
        col_list = cls._db.list_collection_names()

        if col_name not in col_list:
            raise Exception(f"Collection: {col_name} does not exist.")
        else:
            # import all data from collection
            collection = cls._db[col_name]
            class_to_init = globals.col2class.get(col_name)
            df = pd.DataFrame(list(collection.find({})))
            df.drop("_id", axis=1, inplace=True)  # axis = 1 for column and not row

            objects = {}
            # necessary for cls.import_foreign_keys
            col_to_import = [col for col in df.columns if col.endswith("_id")]
            with alive_bar(
                len(df.index), title=f"Importing data from {col_name}"
            ) as bar:
                for row in [df.iloc[idx] for idx in range(len(df.index))]:
                    # If there is at least
                    if len(col_to_import) > 0:
                        # import secondary objects using foreign keys
                        params = cls.import_foreign_keys(row, col_to_import)
                    else:
                        params = row.copy()
                    # print(params)
                    objects[row["id"]] = class_to_init(**params)
                    bar()

        return objects

    def insert_df(cls, collection_name, data_df, upsert, key_id):
        collection = cls._db[collection_name]

        counter = 0

        # Option 1: Update id's that already exist
        if upsert:
            for index, record in data_df.iterrows():
                if record.get(key_id) is None:
                    raise Exception(
                        f"key_id of data to be inserted into collection: '{collection_name}' must be defined"
                    )
                else:
                    collection.replace_one(
                        {key_id: record.get(key_id)}, record.to_dict(), upsert=True
                    )
                    counter += 1

        # Option 2: Duplicate id's that already exist
        else:
            for index, record in data_df.iterrows():
                collection.insert_one(record.to_dict())
                counter += 1

        print(f"Finished {counter} insertions into collection: {collection_name}")

    def make_foreign_keys(cls, df):
        """Change fields that are objects (to be found in other collections) into list of references through id"""

        for column in df.columns:
            # check if single object
            if not meta_fcts.is_a_compound(df[column].iloc[0]):
                for att, my_class in itertools.product(
                    df[column], list(globals.col2class.values())
                ):
                    if isinstance(att, my_class):
                        df[column + "_id"] = [att.id for att in df[column]]
                        df.drop(column, axis=1, inplace=True)
                        break
            else:
                # if compound check if values are objects
                for att, my_class in itertools.product(
                    df[column], list(globals.col2class.values())
                ):
                    if any(
                        isinstance(att_att, my_class)
                        for att_att in meta_fcts.get_values_from_compound(att)
                    ):
                        df[column + "_id"] = [
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

            # get collection name and associated class
            param_name = col[:-3]  # remove '_id'
            if param_name in globals.col2class.keys():
                att_collection_name = param_name
            elif any(col_name in col for col_name in globals.col2class.keys()):
                for col_name in globals.col2class.keys():
                    if col_name in col:
                        att_collection_name = col_name
                        break
            else:
                raise Exception(
                    "The variable name does not contain a valid collection name"
                )
            class_to_import = globals.col2class[att_collection_name]

            # Get foreign key objects
            if meta_fcts.is_a_compound(row[col]):
                att_dicts = list(
                    cls._db[att_collection_name].find(
                        {"id": {"$in": [att_id for att_id in row[col]]}}
                    )
                )
                att_df = pd.DataFrame(att_dicts).drop("_id", axis=1)
                if is_make_dict:
                    att_objects = {
                        att_row["id"]: class_to_import(**att_row)
                        for att_row in [
                            att_df.iloc[idx] for idx in range(len(att_df.index))
                        ]
                    }
                    if len(att_objects) < 1:
                        print("hey")
                else:
                    att_objects = [
                        class_to_import(**att_row)
                        for att_row in [
                            att_df.iloc[idx] for idx in range(len(att_df.index))
                        ]
                    ]
            else:
                att_dicts = cls._db[att_collection_name].find_one({"id": row[col]})
                del att_dicts["_id"]
                if is_make_dict:
                    att_objects = {att_dicts[0]["id"]: class_to_import(**att_dicts[0])}
                else:
                    att_objects = [class_to_import(**att_dicts[0])]

            del params[col]
            params[param_name] = att_objects

            return params
