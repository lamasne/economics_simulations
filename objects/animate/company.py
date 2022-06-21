class Company:
    def __init__(self, ticker, profit, capital, nb_of_shares, id=None):
        self.ticker = ticker
        self.id = id if id is not None else ticker
        self.profit = profit  # $ per year
        self.capital = capital
        self.nb_of_shares = nb_of_shares

    def get_eps(self):
        return self.profit / self.nb_of_shares

    def get_PE(self):
        return self.capital / self.profit

    def get_share_price(self):
        if self.nb_of_shares > 0:
            return self.capital / self.nb_of_shares  # assuming capital is only equity
        else:
            return None

    def change_capital(self, amount):
        self.capital += amount

    def set_nb_shares(self, nb_shares):
        self.nb_of_shares = nb_shares
