import pandas as pd
import meta.repository as repository
import meta.globals as globals


def test_insert_df(collection_name="companies", data_df=None):
    print("Started testing insert_df\n")

    if data_df is None:
        data_df = pd.DataFrame(
            data={
                "ticker": globals.tickers,
                "profit_init": globals.profit_inits,
                "capital_init": globals.capital_inits,
                "nb_shares": globals.nb_shares_inits,
            }
        )

    # Connect to collection
    client = repository._get_client()
    db = repository._get_db(client)
    collection = db[collection_name]

    def print_all_records(collection):
        cursor = collection.find()
        for record in cursor:
            print(record)
        return collection.count_documents({})

    # Check data before insert
    records_before = print_all_records(collection)
    # Execute function to test
    repository.insert_df(collection_name, data_df)
    # check data after insert
    records_after = print_all_records(collection)

    client.close()

    if records_after == records_before + len(data_df.index):
        print("Test successful\n")
        return 1
    else:
        print(
            "Test failed: all the records were not inserted (maybe some were updated?)\n"
        )
        return 0
