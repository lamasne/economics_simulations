import numpy as np
import pandas as pd

class Asset:
    def __init__(self, ticker, start_time, start_price):
        self.ticker = ticker
        prices = pd.DataFrame([[start_price]], columns=['Close'])
        t = pd.DataFrame([[start_time]], columns=['Time'])
        self.prices_df = t.join(prices)

    def get_prices_df(self):
        return self.prices_df

    def get_last_price(self):
        prices = self.get_prices_df()['Close'].values
        return prices[-1]

    def get_ticker(self):
        return self.ticker

    def update_price(self, new_price, new_time):
        df = pd.DataFrame([[new_time, new_price]], columns=['Time', 'Close'])
        self.prices_df = self.get_prices_df().append(df, ignore_index=True)
