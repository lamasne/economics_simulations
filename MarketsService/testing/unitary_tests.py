import pandas as pd
from objects.animate.investment_bank import InvestmentBank
import db_interface.dao_MongoDB as dao_MongoDB
import model_settings as model_settings
from dynamics.main_fcts import *


def test_match_making():
    pass


def test_make_IPO():
    # Get parameters
    ticker = "PEAR"
    companies = generate_companies(get_companies_df())
    shares = generate_shares(companies)
    investors = generate_investors(
        model_settings.nb_investors, shares, companies
    ).values()
    inv_banks = {
        name: InvestmentBank(name, 0, []) for name in ["Morgan Stanley"]
    }.values()

    def get_owners(ticker, investors):
        return list(
            filter(
                lambda inv: [
                    share
                    for share in inv.available_shares.values()
                    if share.ticker == ticker
                ],
                investors,
            )
        )

    # Actual test
    owners_of_PEAR_b = get_owners(ticker, investors)
    make_IPO(companies[ticker], inv_banks, investors)
    owners_of_PEAR_a = get_owners(ticker, investors)
    if not owners_of_PEAR_b and len(owners_of_PEAR_a) > 0:
        return True
    else:
        return False


def test_insert_df():
    collection_name = ("companies",)
    data_df = pd.DataFrame(
        data={
            "ticker": model_settings.tickers,
            "profit_init": model_settings.profit_inits,
            "market_cap_init": model_settings.market_cap_inits,
            "nb_shares": model_settings.nb_shares_inits,
        }
    )

    # Connect to collection
    client = dao_MongoDB._get_client()
    db = dao_MongoDB._get_db(client)
    collection = db[collection_name]

    def print_all_records(collection):
        cursor = collection.find()
        for record in cursor:
            print(record)
        return collection.count_documents({})

    # Check data before insert
    records_before = print_all_records(collection)
    # Execute function to test
    dao_MongoDB.insert_df(collection_name, data_df)
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


if __name__ == "__main__":
    test_match_making()
