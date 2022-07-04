import matplotlib.pyplot as plt
from objects.animate.ea import EA


class MomentumTrader(EA):
    def __init__(self, shares_fk=None, id=None):
        self.id = id
        self.shares_fk = shares_fk if shares_fk is not None else []
        self.money = 1000  # random between 10000 and 100000 maybe

    def place_order(self, short_or_sell, share):
        if short_or_sell == 1:
            if self.money > share.get_last_price():
                self.money -= share.get_last_price()
                self.shares.append(share)
                print(f"Bought {share.get_ticker()} for {share.get_last_price()}")
            else:
                print(f"Not enough money to buy {share.get_ticker()}")
        elif short_or_sell == 2:
            self.money += share.get_last_price()
            self.shares.remove(share)
            print(f"Sold {share.get_ticker()} for {share.get_last_price()}")

        else:
            raise ("Error in placing order")

    # if 1 --> long, if 2 --> short
    def is_momentum_trade(self, asset):
        prices_df = asset.get_prices_df()
        prices_df.ta.macd(
            close="Close", fast=12, slow=26, signal=9, append=True
        )  # 12, 26, 9

        macd = prices_df["MACD_12_26_9"].values
        macds = prices_df["MACDs_12_26_9"].values

        # Strategy 1 of https://school.stockcharts.com/doku.php?id=technical_indicators:moving_average_convergence_divergence_macd
        alpha = 0.5
        dt = 1  # delta t
        if (macd[-1] - macds[-1]) * (
            macd[-2] - macds[-2]
        ) < 0:  # i.e. if MACD crosses signal as TRUE only if the one that was up is now down

            fig, axs = plt.subplots(2)
            fig.suptitle("Momentum trading")
            axs[0].plot(prices_df["Close"])
            axs[1].plot(macd)
            axs[1].plot(macds)

            if macd[-1] > macds[-1]:
                return 1
            else:
                return 2
            # if (macd[-1] - macd[-2]) - (macds[-1] - macds[-2]) > alpha * dt: # ¿ Or d(macd)/dt > alpha*d(macds)/dt ?
            #     return 1
            # elif (macd[-1] - macd[-2]) - (macds[-1] - macds[-2]) < alpha * dt:
            #     return 2

        else:
            return 0
