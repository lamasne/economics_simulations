import numpy as np
from pandas import date_range
from pymongo import MongoClient, ReplaceOne
import pymongo
import meta.globals as globals
import json
import meta.meta_functions as meta_fcts


def import_objects_from_db(col_name):
    client = _get_client()
    db = _get_db(client)
    col_list = db.list_collection_names()

    if col_name not in col_list:
        raise Exception(f"Collection: {col_name} does not exist.")
    else:
        collection = db[col_name]
        class_to_init = globals.col2class.get(col_name)
        records = collection.find({})
        objects = np.empty(collection.count_documents({}), dtype=class_to_init)
        for idx, record in enumerate(records):
            record.pop("_id")
            raise Exception("TO IMPLEMENT: if contains _id --> import object")
            objects[idx] = class_to_init(**record)

    return objects


def create_collection_from_objects(
    col_name, objects, is_from_scratch=False, key_id="id"
):
    """
    Prepare init state of collection in database.
    params:
    - objects: list of objects
    - is_from_scratch: if True, only insert new data, else will keep previous records as part of the new state
    """
    client = _get_client()
    db = _get_db(client)
    col_list = db.list_collection_names()

    if col_name not in col_list:
        print(f"Collection: {col_name} does not exist. It will be created")
    elif is_from_scratch:
        reset_collection(col_name)
    insert_objects(col_name, objects, key_id=key_id)


def create_collection_from_df(
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
    client = _get_client()
    db = _get_db(client)
    col_list = db.list_collection_names()

    if col_name not in col_list:
        print(f"Collection: {col_name} does not exist. It will be created")
    elif is_from_scratch:
        reset_collection(col_name)
    insert_df(col_name, data, upsert=True, key_id=key_id)


def reset_collection(collection_name):
    client = _get_client()
    db = _get_db(client)
    collection = db[collection_name]

    if collection.delete_many({}):
        print(f"Deleted all records from collection: {collection_name}")
    else:
        print(f"Could not delete records from collection: {collection_name}")


def insert_objects(collection_name, objects, key_id):
    client = _get_client()
    db = _get_db(client)
    collection = db[collection_name]

    counter = 0
    for key in objects.keys():
        data_dict = vars(objects[key])

        # Change attributes that are objects into references through id
        for key in data_dict.keys():
            for my_class in list(globals.col2class.values()):
                # if dict check if values are objects
                if isinstance(data_dict[key], dict) and any(
                    isinstance(company, my_class)
                    for company in list(data_dict[key].values())
                ):
                    for key2 in data_dict[key].keys():
                        data_dict[key + "_id"] = data_dict[key]
                        del data_dict[key]
                        data_dict[key + "_id"][key2] = data_dict[key + "_id"][key2].id
                # if other iterable e.g. list or tuples, check if contains any object
                elif meta_fcts.is_iterable(data_dict[key]) and any(
                    isinstance(company, my_class) for company in list(data_dict[key])
                ):
                    for idx in range(0, len(data_dict[key])):
                        data_dict[key + "_id"] = data_dict[key]
                        del data_dict[key]
                        data_dict[key + "_id"][idx] = data_dict[key + "_id"][idx].id
                # if single value, check if it is an object
                elif isinstance(data_dict[key], my_class):
                    data_dict[key] = data_dict[key].id

        if data_dict.get(key_id) is None:
            raise Exception(
                f"key_id of data to be inserted into collection: '{collection_name}' must be defined"
            )

        else:
            collection.replace_one(
                {key_id: data_dict.get(key_id)}, data_dict, upsert=True
            )
            counter += 1

    print(f"Finished {counter} updates/insertions into collection: {collection_name}")
    client.close()


def insert_df(collection_name, data_df, upsert, key_id):
    client = _get_client()
    db = _get_db(client)
    collection = db[collection_name]

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
    client.close()


def _get_db(client):
    db_name = globals.mongodb_settings["db_name"]
    return client[db_name]


def _get_client():
    host = globals.mongodb_settings["host"]
    port = globals.mongodb_settings["port"]
    try:
        client = MongoClient(host, port)
    except:
        print("Could not connect to MongoDB")
    return client
