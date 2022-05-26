import pandas as pd
import numpy as np

class Market:
    def __init__(self):
            self.bid = []
            self.ask = []
    
    def get_order_book(self):
        bid_prices = np.array(self.bid).transpose()[0]
        ask_prices = np.array(self.ask).transpose()[0]
        return pd.DataFrame([[np.sort(bid_prices), np.sort(ask_prices)]], columns=['Bid', 'Ask'])

    def append_bid(self, bid, ea, share):
        self.bid.append([bid, ea, share])
    
    def append_ask(self, ask, ea, share):
        self.ask.append([ask, ea, share])

    # Many assumptions here
    def match_bid_ask(self, share):
        tol = 0.01
        for demand in self.ask:
            for supply in self.bid:
                if demand[0]/supply[0] > 1-tol:
                    seller = supply[1]
                    shere = supply[2]
                    supply[1].sell(sup)
                    self.bid.remove(supply)
                    self.ask.remove(demand)
                    y_s1[idx][0] -= y_d1[idxd][0]
                    y_d1[idx] = 0 
                else:
                    y_d1[idx] -= y_s1[idx]
                    y_s1[idx] = 0
        return [y_d1, y_s1]

    # def match_bid_ask(self):
    #     y_d1 = self.bid.copy()
    #     y_s1 = self.ask.copy()
    #     for idx, elem in enumerate(y_s1):
    #         if y_s1[idx][1] > y_d1[idx][1]:
    #             y_s1[idx] -= y_d1[idx]
    #             y_d1[idx] = 0 
    #         else:
    #             y_d1[idx] -= y_s1[idx]
    #             y_s1[idx] = 0
    #     return [y_d1, y_s1]

    def make_bid_ask_plot(bid_ask_ax, x, y_d0, y_s0, x_label='price', y_label='quantity', title='Demand and supply curves'):
        bid_ask_ax.set(xlabel=x_label, ylabel=y_label)
        bid_ask_ax.set_title(title)
        bid_ask_ax.plot(x, y_d0, 'r-')
        bid_ask_ax.plot(x, y_s0, 'b-')
        return bid_ask_ax