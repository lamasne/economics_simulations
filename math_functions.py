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
    burr_analysis() # supposed to be the best)
    invgauss_analysis()





    # should give 3000, 7500 according to Hellebrandt, T. and Mauro, P., 2015. The future of worldwide income distribution. Peterson Institute for international economics working paper, (15-7).

# whenever I have the real data, to estimate which fit is the best
#    params_1, cov = curve_fit(invgauss.pdf, x, data)



def first_analysis():
    mu = 1
    scale = 1

    r1 = stats.invgauss.rvs(mu, scale=scale, size=1000)
    r2 = stats.skewnorm.rvs(a=5, mu=mu, scale=scale, size=1000) # a = asymetry, mu = mu, scale = std
    r3 = stats.lognorm.rvs(s=0.5, mu=mu, scale=scale, size=1000)
    r4 = stats.burr12.rvs(c=2, d=1, mu=mu, scale=scale, size=1000)

    print(statistics.mean(r4))
    print(statistics.median(r4))


    params_1 = stats.invgauss.fit(r1)
    params_2 = stats.skewnorm.fit(r2)
    params_3 = stats.lognorm.fit(r3)
    params_4 = stats.burr12.fit(r4)

    x = np.linspace(0, mu + 10*scale, 10000)

    plt.plot(x, normalize([stats.invgauss.pdf(x,*params_1)])[0], label='inv_gauss')
    plt.plot(x, normalize([stats.lognorm.pdf(x,*params_3)])[0], label='log_norm')
    plt.plot(x, normalize([stats.skewnorm.pdf(x,*params_2)])[0], label='skewnorm')
    plt.plot(x, normalize([stats.burr12.pdf(x,*params_4)])[0], label='burr12')
    
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
            if (c>d):
                try:
                    moneys_init = stats.burr12.rvs(c=c/10, d=d, mu=mu, scale=scale, size=size)
                    if abs(statistics.mean(moneys_init) -  mu) < 2000:
                        print(statistics.median(moneys_init))
                        print(statistics.mean(moneys_init))
                        params = (stats.burr12.fit(moneys_init))
                        if c <= 10:
                            plt.plot(x, normalize([stats.burr12.pdf(x,*params)])[0], 'r', label=f'c:{c}, d:{d}')
                        elif c <=20:
                            plt.plot(x, normalize([stats.burr12.pdf(x,*params)])[0], 'b',  label=f'c:{c}, d:{d}')
                        else:
                            plt.plot(x, normalize([stats.burr12.pdf(x,*params)])[0], 'k',  label=f'c:{c}, d:{d}')
                except:
                    print(f'{c} and {d} gave an error')

    plt.legend()
    plt.show()


def invgauss_analysis():
    '''
    derivation of parameters for invgauss fitting 
    using a first approx of mean and median from Hellebrandt, T. and Mauro, P., 2015. The future of worldwide income distribution. Peterson Institute for international economics working paper, (15-7).
    '''
    mu_exp, median_exp, size = 7500, 3000, 10000 # 7500, 3000
    x = np.linspace(0, mu_exp + median_exp, size)
    
    nb_scale = 20
    nb_mu = 20
    mu_test = np.linspace(3.1,3.3,nb_mu)
    scale_test = np.linspace(2290,2350,nb_scale)

    tol = 10
    min = 7500

    with alive_bar(nb_mu*nb_scale, title='invgauss_analysis') as bar:
        for mu in mu_test:
            for scale in scale_test:
                moneys_init = stats.invgauss.rvs(mu, scale=scale, size=size)
                if abs(statistics.median(moneys_init) - median_exp) < tol:
                    if abs(statistics.mean(moneys_init) - mu_exp) < tol:
                        if abs(statistics.median(moneys_init) - median_exp) + abs(statistics.mean(moneys_init) - mu_exp) < min:
                            min = abs(statistics.median(moneys_init) - median_exp) + abs(statistics.mean(moneys_init) - mu_exp)
                            idx = f'{mu} - {scale}'
                        params = stats.invgauss.fit(moneys_init)
                        norm_distr = normalize([stats.invgauss.pdf(x,*params)])[0]
                        #if max(norm_distr) < 0.1:
                        print(f'{statistics.median(moneys_init)} - {statistics.mean(moneys_init)}')
                        plt.plot(x, norm_distr, label=f'mu:{mu}, scale:{scale}')
                bar()

    print(f'min: {min} for {idx}')

    plt.legend()
    plt.show()

    moneys_init = stats.invgauss.rvs(mu=3.18, scale=2337, size=size) #--> derivation in math_functions/invgauss_analysis 
    print(f'{statistics.median(moneys_init)} - {statistics.mean(moneys_init)}')
    params = stats.invgauss.fit(moneys_init)
    norm_distr = normalize([stats.invgauss.pdf(x,*params)])[0]
    plt.plot(x, norm_distr)
    plt.show()

    print('hey')
