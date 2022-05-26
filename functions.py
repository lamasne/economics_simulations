import numpy as np
from math import sqrt


# def normal_dist(x, mu, sigma, volume = 1):
#     y = np.exp( - (x - mu)**2 / (2 * sigma**2) )
#     y = volume * y / np.linalg.norm(y)
#     return y 

def get_orders(investors, ticker, news_real_impact, market):
    for investor in investors:
        investor.place_order(ticker, news_real_impact, market)
        yield