import json

import meta.globals as globals
import meta.repository as repository
import pandas as pd
from alive_progress import alive_bar
from objects.animate.investment_bank import InvestmentBank
from objects.animate.market import Market
from dynamics.sub_fcts import *
import meta.meta_functions as meta_fcts


def generate_init_state(is_import=False, is_from_scratch=True, is_save_init=True):
    """
    Init all objects at time t_0
    from then on they should be retrieved from database (and not as arguments)
    """

    object_types = [Company, Share, Market, ValueInvestor, InvestmentBank]
    df = pd.DataFrame(
        {
            "object_type": object_types,
            "col_name": [
                meta_fcts.get_key_from_value(globals.col2class, object_type)
                for object_type in object_types
            ],
            "data": None,
        }
    )

    # import data
    if is_import:
        for idx, col_name in enumerate(df["col_name"]):
            df.iloc[idx]["data"] = repository.import_objects_from_db(col_name)

    else:
        # Generate data
        companies = generate_companies("from_df", get_companies_df())
        shares = generate_shares(companies)
        markets = {"Nasdaq": Market(companies, "Nasdaq")}
        investors = generate_investors(globals.nb_investors, shares, companies)
        inv_banks = {name: InvestmentBank(name, 0, []) for name in ["Morgan Stanley"]}

        df["data"] = [companies, shares, markets, investors, inv_banks]

    # Update data in db
    if not is_import and is_save_init:
        for row in [df.iloc[idx] for idx in range(len(df.index))]:
            repository.create_collection_from_objects(
                row["col_name"],
                row["data"],
                is_from_scratch,
            )

    return df["data"].tolist()


def simulate_exchange(market, investors, inv_banks):
    """
    Starts simulation

    Inputs:
        - timespan: for now it is the number of iterations
    """
    timespan, ticker = (
        globals.timespan,
        globals.tickers[0],
    )

    # Start with IPOs
    make_IPO(market.companies["PEAR"], inv_banks, investors)
    owners_of_PEAR = list(
        filter(
            lambda inv: [
                share for share in inv.available_shares if share.ticker == "PEAR"
            ],
            investors,
        )
    )
    print(f"owners_of_PEAR: {owners_of_PEAR}")

    # Simulate one day at a time
    for j in range(timespan):
        news_real_impact = get_news_real_impact(ticker)
        print(f"FLASH NEWS: {news_real_impact}")

        nb_investors = len(investors)

        with alive_bar(nb_investors, title="Get orders") as bar:
            for i in get_orders(investors, ticker, news_real_impact, market):
                bar()

        market.make_bid_ask_plot()

        # t = pd.date_range(start=start_time, end='2022-10-13', periods=resolution).to_frame(index=False, name='Time')
        market.match_bid_ask(ticker)
        print(
            f"Buy price: {market.get_buy_price(ticker)}\nSell price: {market.get_sell_price(ticker)}"
        )

        market.make_bid_ask_plot()
