from re import A
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

class Market:
    def __init__(self, companies):
            self.bid = []
            self.ask = []
            self.companies = companies
    
    def get_order_book(self):
        if self.bid:
            bid_prices = np.transpose(np.array(self.bid))[0]
        else:
            bid_prices = [0]
        if self.ask:
            ask_prices = np.transpose(np.array(self.ask))[0]
        else:
            ask_prices = [0]            
        return pd.DataFrame([[np.sort(bid_prices), np.sort(ask_prices)]], columns=['Bid', 'Ask'])

    def get_buy_price(self, ticker):
        supplies = self.get_supply_for_ticker(ticker)
        if supplies:
            price = np.array(supplies).transpose()[0]
            return price[0]
        else:
            return 0

    def get_sell_price(self, ticker):
        demands = self.get_demand_for_ticker(ticker)
        if demands:
            price = np.array(demands).transpose()[0]
            return price[0]
        else:
            return 0

    def process_bid(self, bid, ea, ticker):
        if ea.available_money > bid:
            ea.available_money -= bid
            ea.blocked_money += bid
            self.bid.append([bid, ea, ticker])

    def process_ask(self, ask, ea, share):
        # relevant_shares = list(filter(lambda share : share.get_ticker() == ticker, ea.available_shares))
        if share:
            ea.available_shares.remove(share)
            ea.blocked_shares.append(share)
            if not ea.blocked_shares:
                print('ISSUE')
            self.ask.append([ask, ea, share])
    
    # For bid and ask lists
    def get_demand_for_ticker(self, ticker):
        return list(filter(lambda bid: bid[2]==ticker, self.bid))

    def get_supply_for_ticker(self, ticker):
        return list(filter(lambda ask: ask[2].get_ticker() == ticker, self.ask))

    # Many assumptions here
    def match_bid_ask(self, ticker):
        tol = 0.2 #percent --> 0.2 = 20 cent for 100$ stock

        demands = self.get_demand_for_ticker(ticker)
        supplies = self.get_supply_for_ticker(ticker)

        for idx_d, demand in enumerate(demands):
            if supplies:
                min = demand[0]
                i = 0
                for idx_s, supply in enumerate(supplies):
                    if demand[0] > supply[0]:
                        min_tmp = abs(demand[0] - supply[0])
                        if min_tmp < min:
                            min = min_tmp
                            i = idx_s

                if min < tol/100 * demand[0]:

                    supply = supplies[i]

                    price_s = supply[0]
                    price_d = demand[0]
                    seller = supply[1]
                    buyer = demand[1]
                    share = supply[2]

                    supplies.remove(supply) # once investor sold, his ask should be removed

                    seller.sell(share, price_s)
                    buyer.buy(share, price_s)

                    i = 0
                    while (self.ask[i][0] != price_s) or (self.ask[i][1] is not seller) or(self.ask[i][2] is not share):
                        i += 1
                    self.ask.pop(i)
                    
                    i = 0
                    while (self.bid[i][0] != price_d) or (self.bid[i][1] is not buyer) or(self.bid[i][2] != ticker):
                        i += 1
                    self.bid.pop(i)
                    # print(f'{buyer} bought {share} from {seller} for {price_s}')

    def make_bid_ask_plot(self, x_label='price', y_label='quantity', title='Demand and supply curves'):
        order_book = self.get_order_book()
        demand_pdf = order_book['Bid'].values[0]       
        supply_pdf = order_book['Ask'].values[0]
        
        # ax.hist(demand_pdf, bins=50, density=True, histtype='stepfilled', alpha=0.2) #bins = nb of separations (rectangles)

        if len(demand_pdf) > 40 and len(supply_pdf) > 40:  
            sns.displot([demand_pdf, supply_pdf], kde=True, bins=40)
        elif len(demand_pdf) > 40 and len(supply_pdf) < 40:  
            sns.displot(demand_pdf, kde=True, bins=40)
        elif len(supply_pdf) > 40 and len(demand_pdf) < 40:  
            sns.displot(supply_pdf, kde=True, bins=40)
