import numpy as np
import pandas as pd

class Asset:
    def __init__(self, ticker):
        self.ticker = ticker

    def get_ticker(self):
        return self.ticker
