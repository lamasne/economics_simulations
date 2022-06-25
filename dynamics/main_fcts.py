import json

import meta.globals as globals
from meta.repository import DB_interface
import pandas as pd
from alive_progress import alive_bar
from objects.animate.investment_bank import InvestmentBank
from objects.animate.market import Market
from dynamics.sub_fcts import *
import meta.meta_functions as meta_fcts


def generate_init_state(is_import=False, is_save_init=True):
    """
    Init all objects at time t_0
    """

    object_types = [Company, Market, Share, ValueInvestor, InvestmentBank]
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

    # Import data
    if is_import:
        db_interface = DB_interface(globals.mongodb_settings)
        for idx, col_name in enumerate(df["col_name"]):
            df.iloc[idx]["data"] = db_interface.read_collection(col_name)

    # Generate data
    else:
        companies = generate_companies(get_companies_df())
        markets = {"Nasdaq": Market(companies, "Nasdaq")}
        shares = generate_shares(companies)
        investors = generate_investors(globals.nb_investors, shares, companies)
        inv_banks = {name: InvestmentBank(name, 0, []) for name in ["Morgan Stanley"]}

        df["data"] = [companies, markets, shares, investors, inv_banks]

    # Update data in db
    if not is_import and is_save_init:
        db_interface = DB_interface(globals.mongodb_settings)
        for row in [df.iloc[idx] for idx in range(len(df.index))]:
            db_interface.update_collection(
                row["col_name"],
                row["data"],
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

    # Simulate one day at a time
    for j in range(timespan):
        news_real_impact = get_news_real_impact(ticker)
        print(f"FLASH NEWS: {news_real_impact}")

        nb_investors = len(investors)

        with alive_bar(nb_investors, title="Get orders") as bar:
            for _ in get_orders(investors, ticker, news_real_impact, market):
                bar()

        market.make_bid_ask_plot()

        # t = pd.date_range(start=start_time, end='2022-10-13', periods=resolution).to_frame(index=False, name='Time')
        market.match_bid_ask(ticker)
        print(
            f"Buy price: {market.get_buy_price(ticker):.2f}\nSell price: {market.get_sell_price(ticker):.2f}"
        )

        market.make_bid_ask_plot()
