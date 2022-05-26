
class Company:
    def __init__(self, ticker, profit_init, nb_of_shares) -> None:
        self.profit = profit_init # $ per year
        self.ticker = ticker
        self.nb_of_shares = nb_of_shares

    def get_eps(self):
        return self.profit/self.nb_of_shares