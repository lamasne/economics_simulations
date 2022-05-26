import numpy as np
import matplotlib.pyplot as plt

# returns the best prediction of impact on the company's profit in 1 year ( 
# i.e. returns: \tilde{profit}(t+1) / profit(t)
# == 1 --> no impact
# > 1 --> gain
# < 1 --> loss
def get_news_real_impact(ticker): 
    mu = 1; sigma = 0.1
    # s = np.random.normal(mu, sigma, 1000)
    # count, bins, ignored = plt.hist(s, 30, density=True)
    # plt.plot(bins, 1/(sigma * np.sqrt(2 * np.pi)) *
    #             np.exp( - (bins - mu)**2 / (2 * sigma**2) ),
    #         linewidth=2, color='r')

    return np.random.normal(mu, sigma, 1)[0]