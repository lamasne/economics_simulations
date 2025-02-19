from audioop import avg
from math import ceil
import db_interface.investors_repo
import db_interface.market_repo
import sys
import time
import concurrent.futures  # multi threading/processing
from dao_pymongo.dao import Dao
from dynamics.market_consumer import MarketConsumer
import meta.meta_functions as meta_fcts
from objects.animate.investment_bank import InvestmentBank
from objects.animate.company import Company
from objects.animate.market import Market
from objects.inanimate.share import Share
from objects.animate.value_investor import ValueInvestor
import meta.settings.model_settings as model_settings
import numpy as np
import pandas as pd
import random
from alive_progress import alive_bar
import scipy as sp
from scipy import stats
from sklearn.preprocessing import normalize
import matplotlib.pyplot as plt
import seaborn as sns
import statistics
import json
import os


def simulate_exchange():
    """
    Starts simulation

    Inputs:
        - timespan: for now it is the number of iterations
    """

    initialize()

    make_IPO()

    # Simulate one day at a time (or time delta?)
    for _ in range(model_settings.timespan):

        ## If a potentially impactful news for the future of a company is made public, trigger traders
        # Probability of such an event to occur - because there are 21 price jumps a year on avg according to: Lee, Suzanne S. "Jumps and information flow in financial markets." The Review of Financial Studies 25.2 (2012): 439-479.
        # Note: the time at which the news is made public should be a distribution with higher probability at market closing (earnings, dividends, etc.)

        # if random.randint(1, 365) <= 21:
        news_real_impact = get_news()
        print(f"FLASH NEWS: {news_real_impact}")
        # Make investors react to news
        investors = Dao().read_collection(ValueInvestor)
        with alive_bar(len(investors), title="Get orders") as bar:
            for investor in investors.values():
                investor.react_to_news(news_real_impact)
                bar()

        # 9:28 --> Nasdaq's opening cross, cf. https://money.howstuffworks.com/opening-closing-cross.htm + Nasdaq official doc

        # For now focus on AAPL in Nasdaq (because studied news is about this ticker-market pair)
        market = Dao().read_objects(Market, ["Nasdaq"])["Nasdaq"]
        ticker = "AAPL"

        # t = pd.date_range(start=start_time, end='2022-10-13', periods=resolution).to_frame(index=False, name='Time')

        # The matching (and ploting) shall be orders (matching) listeners probably
        market.match_bid_ask(ticker)
        print(f"Best price: {market.get_buy_price(ticker)}")
        market.make_bid_ask_plot()


def initialize():

    # Database and back-up
    if not model_settings.is_import:
        generate_init_state()
        Dao().backup_db()
    else:
        Dao().restore_backup()
    print("\n")
    db_interface.market_repo.MarketRepo().create_index_match_making()

    # Start event consumers (EDA)
    try:
        # Just one exchange for now (each might have its own consumer in the future)
        td = MarketConsumer("Nasdaq")
        td.start()
    except Exception as e:
        raise Exception(
            "Unable to start thread that processes orders in market:\n" + str(e)
        )


def generate_init_state():
    """
    Init all objects at time t_0 in the db
    """
    # Define what has to be initialized <-- change by object_types = globals.col2class.values()?
    object_types = [Company, Market, Share, ValueInvestor, InvestmentBank]

    companies = generate_companies(get_companies_df())
    print("Generated companies")
    markets = {"Nasdaq": Market(list(companies.keys()), "Nasdaq")}
    print("Generated market")
    shares = generate_shares(companies)
    print("Generated shares")
    investors = generate_investors(model_settings.nb_investors, shares, companies)
    print("Generated investors")
    inv_banks = {name: InvestmentBank(name, 0, []) for name in ["Morgan Stanley"]}
    print("Generated investment bank")

    df = pd.DataFrame(
        {
            "object_type": object_types,
            "data": [companies, markets, shares, investors, inv_banks],
        }
    )

    # Generate data MUST MATCH list object_types
    check_init_state(df["data"].to_list(), object_types)

    # Update data in db
    dao = Dao()
    dao.drop_db()
    print("Dropped whole database")
    for row in list(df.to_dict(orient="index").values()):
        dao.create_objects(
            row["object_type"],
            row["data"],
        )
    print("Recreated whole database")


def check_init_state(data_generated, data_to_generate):
    """If data generated do not match object_types, return error"""
    if len(data_generated) != len(data_to_generate):
        raise Exception("Not all collections have been initialized (or too many)")
    if not all(
        isinstance(list(data_generated[i].values())[0], object_type)
        for i, object_type in enumerate(data_to_generate)
    ):
        raise Exception("Mismatch between collections required and data generated")


def get_companies_df():
    companies_data = pd.DataFrame(
        data={
            "ticker": model_settings.tickers,
            "profit_init": model_settings.profit_inits,
            "market_cap_init": model_settings.market_cap_inits,
            "nb_shares": model_settings.nb_shares_inits,
            "capital": 0,
        }
    )  # Maybe make it a JSON in the future (when there are more data)
    # print(f"Companies data:\n {companies_data}")

    return companies_data


def generate_companies(data=None):
    """
    output: dict --> dict[company_id] = company
    params:
    - companies_data = Dataframe only for now
    """
    if isinstance(data, pd.DataFrame):
        # If data is always in the right order, following lines could be replaced by:
        # companies = {Company(*row.values()) for row in list(data.to_dict(orient="index").values())}
        companies = {}
        for row in list(data.to_dict(orient="index").values()):
            ticker = row["ticker"]
            companies[ticker] = Company(
                ticker,
                row["profit_init"],
                row["market_cap_init"],
                row["nb_shares"],
                row["capital"],
            )  # private company if nb_share = 0
    else:
        raise Exception("Wrong format of input data")

    return companies


def generate_shares(companies):
    """
    input = dict(Company): dict[company_id] = company
    output = dict(Share): dict[share_id] = share
    """
    # shares = np.empty(len(companies.keys()), dtype=Share)
    shares = {}
    for key in companies.keys():
        company = companies[key]
        for i in range(int(company.nb_of_shares)):
            share_id = key + "_" + str(i)
            shares[share_id] = Share(share_id, key)
    return shares


def generate_investors(nb_investors, shares, companies):
    """
    make market_cap and income based on data such as gross domestic savings
    comparison of fit in math_functions.study_distribs
    """
    # Get world wealth distribution
    moneys_init = stats.invgauss.rvs(
        mu=3.18, scale=2337, size=nb_investors
    )  # --> derivation in math_functions/invgauss_analysis
    # moneys_init = stats.invgauss.rvs(c=1, d=1, scale=scale, size=nb_investors)

    print(f"Total money in the market: {sum(moneys_init)}")

    investors = [
        ValueInvestor(moneys_init[i], id=i) for i in range(nb_investors)
    ]  # init with no shares

    # Distribute shares randomly to who can afford it
    for company in list(companies.values()):
        company_shares = [
            share for share in list(shares.values()) if share.ticker == company.ticker
        ]
        price_IPO = 100  # to be changed obviously
        distribute_shares_randomly(company_shares, investors, price_IPO, company)

    return {investor.id: investor for investor in investors}


def make_IPO():
    """Generate initial public offering
    1. Evalutation of company by underwriter, e.g. Morgan Stanley --> initial S-1 with SEC
    2. Evaluation of investors demand for shares by underwriter (shares sold at price 1 discounted) with marketing (Roadshow) --> Update S-1
    3. Price discovery (first investors to sell to other investors)
    """

    # Import objects
    dao = Dao()
    company = dao.read_collection(Company)["PEAR"]
    inv_banks = list(dao.read_collection(InvestmentBank).values())

    # 1
    inv_bank = random.choice(tuple(inv_banks))  # choose inv_bank
    [potential_market_cap, potential_nb_shares] = inv_bank.evaluate_company(company)
    discount = 0.2
    price = (1 - discount) * potential_market_cap / potential_nb_shares

    # 2 - for now sell randomly to richest investors
    shares = [
        Share(company.ticker + "_" + str(i), company.ticker)
        for i in range(potential_nb_shares)
    ]
    dao.create_objects(Share, shares)

    company.set_nb_shares(potential_nb_shares)

    # get potential buyers
    investors = db_interface.investors_repo.InvestorRepo().get_richest_investors()
    distribute_shares_randomly(shares, investors, price, company)

    print("IPO finished")


def distribute_shares_randomly(
    shares, investors, price, company
):  # company should be imported from database
    undistributed_shares = [
        share for share in shares
    ]  # not just shares because I want to keep a copy of share
    unserved_investors = [
        investor for investor in investors
    ]  # not just shares because I want to keep a copy of share

    avg_nb_shares = ceil(len(shares) / len(investors))
    print(f"Average number of shares per investor: {avg_nb_shares}")

    with alive_bar(len(undistributed_shares), title="Distribute shares to rich") as bar:
        while len(undistributed_shares) > 0:
            if len(unserved_investors) < 1:
                unserved_investors = [
                    investor for investor in investors
                ]  # if all have been served, start again the round
            idx_interested_investor = random.randint(0, len(unserved_investors) - 1)
            interested_investor = unserved_investors[idx_interested_investor]
            nb_shares_tmp = random.randint(0, 2 * avg_nb_shares)
            # If there is not enough shares left to distribute, give max
            if len(undistributed_shares) < nb_shares_tmp:
                nb_shares_tmp = len(undistributed_shares)
            for _ in range(nb_shares_tmp):
                if interested_investor.available_money >= price:
                    interested_investor.exchange_money(price)
                    undistributed_shares[0].update_owner(interested_investor.id)
                    company.change_market_cap(price)
                    undistributed_shares.remove(undistributed_shares[0])
                else:
                    # investor does not have enough money
                    break
                bar()
            unserved_investors.remove(
                interested_investor
            )  # to avoid giving the same investor the opportunity to buy too many shares

    # print(len(undistributed_shares))
    # print(len(shares))


# def distribute_shares_randomly(
#     shares, investors, price, company
# ):  # company should be imported from database
#     undistributed_shares = [
#         share for share in shares
#     ]  # not just shares because I want to keep a copy of share
#     unserved_investors = [
#         investor for investor in investors
#     ]  # not just shares because I want to keep a copy of share

#     with alive_bar(len(undistributed_shares), title="Distribute shares to rich") as bar:
#         while len(undistributed_shares) > 0:
#             if len(unserved_investors) < 1:
#                 unserved_investors = [
#                     investor for investor in investors
#                 ]  # if all have been served, start again the round
#             idx_interested_investor = random.randint(0, len(unserved_investors) - 1)
#             interested_investor = unserved_investors[idx_interested_investor]
#             nb_shares_tmp = random.randint(0, 3)
#             if len(undistributed_shares) < nb_shares_tmp:
#                 nb_shares_tmp = len(undistributed_shares)
#             for _ in range(nb_shares_tmp):
#                 interested_investor.exchange_money(price)
#                 undistributed_shares[0].update_owner(interested_investor.id)
#                 company.change_market_cap(price)
#                 undistributed_shares.remove(undistributed_shares[0])
#                 bar()
#             unserved_investors.remove(
#                 interested_investor
#             )  # to avoid giving the same investor the opportunity to buy too many shares

#     # print(len(undistributed_shares))
#     # print(len(shares))


def get_news():
    """
    returns the best prediction of impact on the company's profit in 1 year (
    i.e. returns: \tilde{profit}(t+1) / profit(t)
    == 1 --> no impact
    > 1 --> gain
    < 1 --> loss
    """
    mu = 1
    sigma = 0.1
    news = {}
    news["impact"] = np.random.normal(mu, sigma, 1)[0]
    news["market_id"] = "Nasdaq"
    news["ticker"] = "AAPL"
    return news
