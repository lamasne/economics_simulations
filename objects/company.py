

class Company:
    def __init__(self, ticker, profit_init, capital_init, nb_of_shares):
        self.ticker = ticker
        self.profit = profit_init # $ per year
        self.capital = capital_init
        self.nb_of_shares = nb_of_shares

    def get_eps(self):
        return self.profit/self.nb_of_shares

    def get_PE(self):
        return self.capital/self.profit

    def get_share_price(self):
        return self.capital/self.nb_of_shares # assuming capital is only equity

    def change_capital(self, amount):
        self.capital += amount
    
    def set_nb_shares(self, nb_shares):
        self.nb_of_shares = nb_shares