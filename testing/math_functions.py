import os

import meta.meta_functions as meta_functions
import seaborn as sns
from math import floor
from alive_progress import alive_bar
from scipy import stats
import statistics
from scipy.optimize import curve_fit
from sklearn.preprocessing import normalize
import matplotlib.pyplot as plt
import numpy as np


def study_distribs():
    # Typically wealth and income distribution are fitted by:
    # - singh-maddala distribution:
    #       - Singh, S.; Maddala, G. (1976). "A Function for the Size Distribution of Incomes". Econometrica. 44 (5): 963–970. doi:10.2307/1911538. JSTOR 1911538
    #       - https://www.sciencedirect.com/science/article/pii/S1544612321001045
    # - lognormal gaussian
    # But the best quick fit I have for now is invgauss
    # Data can be found in Hellebrandt, T. and Mauro, P., 2015. The future of worldwide income distribution. Peterson Institute for international economics working paper, (15-7).

    first_analysis()
    burr_analysis()  # supposed to be the best)
    invgauss_analysis()
    capital_distribution()

    # should give 3000, 7500 according to Hellebrandt, T. and Mauro, P., 2015. The future of worldwide income distribution. Peterson Institute for international economics working paper, (15-7).


# whenever I have the real data, to estimate which fit is the best
#    params_1, cov = curve_fit(invgauss.pdf, x, data)


def first_analysis():
    mu = 1
    scale = 1

    r1 = stats.invgauss.rvs(mu, scale=scale, size=1000)
    r2 = stats.skewnorm.rvs(
        a=5, loc=mu, scale=scale, size=1000
    )  # a = asymetry, mu = mu, scale = std
    r3 = stats.lognorm.rvs(s=0.5, loc=mu, scale=scale, size=1000)
    r4 = stats.burr12.rvs(c=2, d=1, loc=mu, scale=scale, size=1000)

    print(statistics.mean(r4))
    print(statistics.median(r4))

    params_1 = stats.invgauss.fit(r1)
    params_2 = stats.skewnorm.fit(r2)
    params_3 = stats.lognorm.fit(r3)
    params_4 = stats.burr12.fit(r4)

    x = np.linspace(0, mu + 10 * scale, 10000)

    plt.plot(x, normalize([stats.invgauss.pdf(x, *params_1)])[0], label="inv_gauss")
    plt.plot(x, normalize([stats.lognorm.pdf(x, *params_3)])[0], label="log_norm")
    plt.plot(x, normalize([stats.skewnorm.pdf(x, *params_2)])[0], label="skewnorm")
    plt.plot(x, normalize([stats.burr12.pdf(x, *params_4)])[0], label="burr12")

    plt.legend()
    plt.show()


def burr_analysis():
    mu, scale, size = 7500, 3000, 10000
    # moneys_init = stats.invgauss.rvs(mu, scale, size=nb_investors)
    x = np.linspace(0, mu + scale, size)

    for c in range(0, 30, 1):
        for d in range(0, 10, 1):
            if d == 0:
                d += 1
            if c > d:
                try:
                    moneys_init = stats.burr12.rvs(
                        c=c / 10, d=d, mu=mu, scale=scale, size=size
                    )
                    if abs(statistics.mean(moneys_init) - mu) < 2000:
                        print(statistics.median(moneys_init))
                        print(statistics.mean(moneys_init))
                        params = stats.burr12.fit(moneys_init)
                        if c <= 10:
                            plt.plot(
                                x,
                                normalize([stats.burr12.pdf(x, *params)])[0],
                                "r",
                                label=f"c:{c}, d:{d}",
                            )
                        elif c <= 20:
                            plt.plot(
                                x,
                                normalize([stats.burr12.pdf(x, *params)])[0],
                                "b",
                                label=f"c:{c}, d:{d}",
                            )
                        else:
                            plt.plot(
                                x,
                                normalize([stats.burr12.pdf(x, *params)])[0],
                                "k",
                                label=f"c:{c}, d:{d}",
                            )
                except:
                    print(f"{c} and {d} gave an error")

    plt.legend()
    plt.show()


def invgauss_analysis():
    """
    derivation of parameters for invgauss fitting
    using a first approx of mean and median from Hellebrandt, T. and Mauro, P., 2015. The future of worldwide income distribution. Peterson Institute for international economics working paper, (15-7).
    """
    mu_exp, median_exp, size = 7500, 3000, 10000  # 7500, 3000
    x = np.linspace(0, mu_exp + median_exp, size)

    nb_scale = 20
    nb_mu = 20
    mu_test = np.linspace(3.1, 3.3, nb_mu)
    scale_test = np.linspace(2290, 2350, nb_scale)

    tol = 10
    min = 7500

    with alive_bar(nb_mu * nb_scale, title="invgauss_analysis") as bar:
        for mu in mu_test:
            for scale in scale_test:
                moneys_init = stats.invgauss.rvs(mu, scale=scale, size=size)
                if abs(statistics.median(moneys_init) - median_exp) < tol:
                    if abs(statistics.mean(moneys_init) - mu_exp) < tol:
                        if (
                            abs(statistics.median(moneys_init) - median_exp)
                            + abs(statistics.mean(moneys_init) - mu_exp)
                            < min
                        ):
                            min = abs(
                                statistics.median(moneys_init) - median_exp
                            ) + abs(statistics.mean(moneys_init) - mu_exp)
                            idx = f"{mu} - {scale}"
                        params = stats.invgauss.fit(moneys_init)
                        norm_distr = normalize([stats.invgauss.pdf(x, *params)])[0]
                        # if max(norm_distr) < 0.1:
                        print(
                            f"{statistics.median(moneys_init)} - {statistics.mean(moneys_init)}"
                        )
                        plt.plot(x, norm_distr, label=f"mu:{mu}, scale:{scale}")
                bar()

    print(f"min: {min} for {idx}")

    plt.legend()
    plt.show()

    moneys_init = stats.invgauss.rvs(
        mu=3.18, scale=2337, size=size
    )  # --> derivation in math_functions/invgauss_analysis
    print(f"{statistics.median(moneys_init)} - {statistics.mean(moneys_init)}")
    params = stats.invgauss.fit(moneys_init)
    norm_distr = normalize([stats.invgauss.pdf(x, *params)])[0]
    plt.plot(x, norm_distr)
    plt.show()

    print("hey")


def capital_distribution():
    scaling_fact = 10e-6

    total_money_in_market = 1e14  # cf. "Market capitalization of listed domestic companies (current US$)". The World Bank.
    total_money_out_market = 1e14  # Intuitive quick approximation = Market participants money apart from stocks e.g. in banks, in physical assets, etc.
    total_money = (
        total_money_in_market + total_money_out_market
    )  # Market participants money apart from stocks
    richest_company = 2e12  # AAPL
    richest_person = 2e11  # Jeff Bezo
    nb_companies = 5e4  # statista

    nb_inv_banks = 1e4
    nb_mutual_funds = 1.2e5  # Worldwide; ICI; IIFA; 2007 to 2021; End of year data - #https://www.statista.com/statistics/278303/number-of-mutual-funds-worldwide/
    nb_market_makers = 1e3
    nb_hedge_funds = 2.5e5  # https://www.hedgeweek.com/2022/03/22/313066/new-analysis-shows-hedge-fund-industry-booming#:~:text=New%20in%2Ddepth%20analysis%20by,27%2C255%20active%20hedge%20funds%20globally.
    nb_financial_institutions = int(
        nb_mutual_funds + nb_market_makers + nb_hedge_funds + nb_inv_banks
    )

    nb_retail_investor = 1e8

    #################################
    # size = int(scaling_fact * nb_retail_investor)
    # moneys_init = stats.invgauss.rvs(900, scale=30, size=size)
    # print("total capital retail: {:e}".format(sum(moneys_init) / scaling_fact))  #
    # print(
    #     "max retail capital: {:e}".format(max(moneys_init) / scaling_fact)
    # )  # Jeff Bezo

    # g = sns.displot(moneys_init, kde=True, bins=40, log_scale=True)
    # # g.set(xlim=(0, 1e10))

    ##################################
    moneys_init_institutional = stats.skewnorm.rvs(
        a=5e3, loc=1e5, scale=1e5, size=nb_financial_institutions
    )
    print("total capital instit: {:e}".format(sum(moneys_init_institutional)))  #
    print(
        "max instit capital: {:e}".format(max(moneys_init_institutional))
    )  # AAPL or ICBC - https://www.google.com/search?q=market+capitalization+by+company&rlz=1C1BNSD_enES988ES988&hl=en&sxsrf=ALiCzsYa4S4VwXDzlgdK_NkagqTVMre1qQ:1659032936715&source=lnms&tbm=isch&sa=X&ved=2ahUKEwjk-fOmm5z5AhUT_RoKHaqBBIAQ_AUoAXoECAEQAw&biw=1536&bih=750&dpr=1.25#imgrc=wK4EBcs4QTxPrM

    f = sns.displot(moneys_init_institutional, kde=True, bins=40, log_scale=True)

    ###################################
    # Print into pdf
    meta_functions.multipage(
        os.path.normpath(
            "C:/Users/Lamas/workspace/PROJECTS/economics/simulation/outputs/hey.pdf"
        )
    )

    plt.show()

    print("hey")


if __name__ == "__main__":
    capital_distribution()
