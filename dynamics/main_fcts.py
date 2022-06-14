from objects.investment_bank import InvestmentBank
from objects.market import Market
import globals
from dynamics.other_fcts import *

import pandas as pd
from alive_progress import alive_bar



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
