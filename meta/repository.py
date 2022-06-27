import time
import itertools
import pandas as pd
from pymongo import MongoClient, UpdateOne
import meta.globals as globals
import meta.meta_functions as meta_fcts
from alive_progress import alive_bar


# singleton to only open connection once
class DB_interface:
    _instance = None
    _client = None
    _db = None

    def __new__(cls):
        """
        Create connection to db in a singleton manner
        """
        settings = globals.mongodb_settings
        if cls._instance is None:
            cls._instance = super(DB_interface, cls).__new__(cls)
            host = settings["host"]
            port = settings["port"]
            try:
                cls._client = MongoClient(host, port)
                print("Created DB interface")
            except:
                raise Exception("Could not connect to MongoDB")

            db_name = settings["db_name"]
            cls._db = cls._client[db_name]

            return cls._instance

    def create_collection(cls, col_name, data, key_id="id"):
        data_df = cls.format_input_data(data)
        cls.validate_data(data_df, key_id)
        data_df = cls.make_foreign_keys(data_df)
        formated_data = [row for row in list(data_df.to_dict(orient="index").values())]
        collection = cls._db[col_name]
        collection.insert_many(formated_data)
        print(f"Created collection: {col_name}")

    def read_collection(cls, col_name):
        col_list = cls._db.list_collection_names()
        if col_name not in col_list:
            raise Exception(f"Collection: {col_name} does not exist.")
        else:
            # import all data from collection
            class_to_init = globals.col2class.get(col_name)
            collection = cls._db[col_name]
            df = pd.DataFrame(list(collection.find({})))
            df.drop("_id", axis=1, inplace=True)  # axis = 1 for column and not row

            # import foreign keys and make objects (call constructors)
            objects = {}
            col_to_import = [
                col for col in df.columns if col.endswith("_id")
            ]  # necessary for cls.import_foreign_keys
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

    def update_collection(cls, col_name, data, key_id="id"):
        """
        Save objects in database, object-attributes are saved as foreign keys through their id
        params:
        - objects: list of objects
        """
        if cls._db.drop_collection(cls._db[col_name]):
            print(f"Dropped collection: {col_name}")
        else:
            print(f"Collection: {col_name} does not exist. It will be created.")
        cls.create_collection(col_name, data, key_id="id")

    def update_objects(cls, col_name, data, key_id):
        """
        updating is about a 100 times slower than inserting, so make sure that's necessary
        """
        data_df = cls.format_input_data(data)
        cls.validate_data(data_df, key_id)
        data_df = cls.make_foreign_keys(data_df)
        formated_data = [row for row in list(data_df.to_dict(orient="index").values())]
        print(
            f"Updating {len(data_df.index)} objects into collection: {col_name}.\nHave you considered using update_collection()?"
        )
        start = time.time()
        cls._db[col_name].bulk_write(
            [
                UpdateOne(
                    {"id": object[key_id]},
                    {"$setOnInsert": object},
                    upsert=True,
                )
                for object in formated_data
            ]
        )
        end = time.time()
        print(f"Collection: {col_name} updated in {end-start:.2f} seconds")

    def make_foreign_keys(cls, df):
        """Change fields that are objects (to be found in other collections) into list of references through id"""

        for column in df.columns:
            # check if single object
            if not meta_fcts.is_compound(df[column].iloc[0]):
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
            param_name = col[:-3]  # remove '_id'

            # get collection name and associated class
            if param_name in globals.col2class.keys():
                att_collection_name = param_name
            else:
                for col_name in globals.col2class.keys():
                    if col_name in col:
                        att_collection_name = col_name
                        break
            if att_collection_name is None:
                raise Exception(
                    "The variable name does not contain a valid collection name"
                )
            class_to_import = globals.col2class[att_collection_name]

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
        if data is a list of objects, make it a dataframe. If not dataframe nor compound of objects --> Exception
        """
        if isinstance(data, pd.DataFrame):
            return data
        elif meta_fcts.is_compound(data):
            data_list = meta_fcts.get_values_from_compound(data)
            if any(
                isinstance(data_list[0], my_class)
                for my_class in globals.col2class.values()
            ):
                return pd.DataFrame.from_records([vars(object) for object in data_list])
        raise Exception("Wrong format of objects to be saved")
