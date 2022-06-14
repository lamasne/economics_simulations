from objects.investment_bank import InvestmentBank
from objects.company import Company
from objects.market import Market
from objects.asset import Asset
from objects.value_investor import ValueInvestor
import globals

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



def generate_init_state():
    '''
    Init all objects at time t_0
    from then on they should be retrieved from database (and not as arguments)
    '''
    companies_data = pd.DataFrame(data={'ticker': globals.tickers, 
                                    'profit_init': globals.profit_inits, 
                                    'capital_init': globals.capital_inits, 
                                    'nb_shares': globals.nb_shares_inits
                                    }) # Maybe make it a JSON in the future (when there are more data)
    
    print(f'Companies data:\n {companies_data}')

    companies = generate_companies(companies_data)
    shares = generate_shares(companies)
    
    market = Market(companies)

    investors = generate_investors(globals.nb_investors, shares, companies)

    inv_banks = [InvestmentBank('Morgan Stanley',0,[])]

    make_IPO(companies['PEAR'], inv_banks, investors)

    owners_of_PEAR = list(filter(lambda inv : [share for share in inv.available_shares if share.ticker == 'PEAR'], investors))
    print(f'owners_of_PEAR: {owners_of_PEAR}')

    return [market, investors]


def generate_companies(companies_data):
    #companies = np.empty(len(companies_data), dtype=Company)
    companies = {}
    for i in range(len(companies_data)):
        ticker = companies_data.iloc[i]['ticker']
        companies[ticker] = Company(ticker, 
                                companies_data.iloc[i]['profit_init'], 
                                companies_data.iloc[i]['capital_init'],
                                companies_data.iloc[i]['nb_shares']) # private company if nb_share = 0
    return companies


def generate_shares(companies_dict):
    companies = list(companies_dict.values())
    shares = np.empty(len(companies), dtype=Asset)
    for idx,company in enumerate(companies):
        shares[idx] = [Asset(company.ticker) for i in range(int(company.nb_of_shares))]
    return shares


def generate_investors(nb_investors, shares, companies):
    '''
    make capital and income based on data such as gross domestic savings
    comparison of fit in math_functions.study_distribs
    '''
    # Get world wealth distribution
    moneys_init = stats.invgauss.rvs(mu=3.18, scale=2337, size=nb_investors) #--> derivation in math_functions/invgauss_analysis 
    # moneys_init = stats.invgauss.rvs(c=1, d=1, scale=scale, size=nb_investors)

    investors = [ValueInvestor(moneys_init[i], []) for i in range(nb_investors)]
    for idx, company in enumerate(list(companies.values())):
        distribute_shares_randomly(shares[idx], investors, company.get_share_price(), company)

    return investors


def make_IPO(company, inv_banks, investors):
    '''Generate initial public offering
    1. Evalutation of company by underwriter, e.g. Morgan Stanley --> initial S-1 with SEC
    2. Evaluation of investors demand for shares by underwriter (shares sold at price 1 discounted) with marketing (Roadshow) --> Update S-1
    3. Price discovery (first investors to sell to other investors)
    '''
    # 1
    inv_bank = random.choice(tuple(inv_banks)) # choose inv_bank
    [potential_capital, potential_nb_shares] = inv_bank.evaluate_company(company)
    discount = 0.2
    price = (1-discount) * potential_capital/potential_nb_shares

    # 2 - for now sell randomly to richest investors
    shares = [Asset(company.ticker) for i in range(potential_nb_shares)]
    company.set_nb_shares(potential_nb_shares)

    money_threshold_top_5 = np.percentile([investor.available_money for investor in investors],95)
    print(f'money threshold to be part of the top 5 investors: {money_threshold_top_5}')
    potential_investors = list(filter(lambda investor:investor.available_money >= money_threshold_top_5, investors))
    
    distribute_shares_randomly(shares, investors, price, company)

    print('IPO finished')


def distribute_shares_randomly(shares, investors, price, company): #company should be imported from database
    undistributed_shares = [share for share in shares] # not just shares because I want to keep a copy of share
    unserved_investors = [investor for investor in investors] # not just shares because I want to keep a copy of share
    
    while len(undistributed_shares) > 0:
        if len(unserved_investors) < 1:
            unserved_investors =   [investor for investor in investors] # if all have been served, start again the round
        idx_interested_investor = random.randint(0,len(unserved_investors)-1)
        interested_investor = unserved_investors[idx_interested_investor]
        nb_shares_tmp = random.randint(0,3)
        if len(undistributed_shares) >= nb_shares_tmp:
            for i in range(nb_shares_tmp):
                confirm_transaction = interested_investor.buy(undistributed_shares[0], price, through_3rd_party = False)
                if confirm_transaction:
                    company.change_capital(price)
                    undistributed_shares.remove(undistributed_shares[0])
            unserved_investors.remove(interested_investor) # to avoid giving the same investor the opportunity to buy too many shares

    # print(len(undistributed_shares))
    # print(len(shares))


def simulate_exchange(market, investors):
    '''
    Starts simulation
    
    Inputs:  
        - timespan: for now it is the number of iterations
    '''
    timespan, ticker = globals.timespan, globals.tickers[0],

    for j in range(timespan):
        news_real_impact = get_news_real_impact(ticker)
        print(f'FLASH NEWS: {news_real_impact}')

        nb_investors = len(investors)

        with alive_bar(nb_investors, title='Get orders') as bar:
            for i in get_orders(investors, ticker, news_real_impact, market):
                bar()

        market.make_bid_ask_plot()

        # t = pd.date_range(start=start_time, end='2022-10-13', periods=resolution).to_frame(index=False, name='Time')
        market.match_bid_ask(ticker)
        print(f'Buy price: {market.get_buy_price(ticker)}\nSell price: {market.get_sell_price(ticker)}')

        market.make_bid_ask_plot()


def get_orders(investors, ticker, news_real_impact, market):
    for investor in investors:
        investor.place_order(ticker, news_real_impact, market)
        yield


def get_news_real_impact(ticker): 
    '''
    returns the best prediction of impact on the company's profit in 1 year ( 
    i.e. returns: \tilde{profit}(t+1) / profit(t)
    == 1 --> no impact
    > 1 --> gain
    < 1 --> loss
    '''
    mu = 1; sigma = 0.1
    return np.random.normal(mu, sigma, 1)[0]        