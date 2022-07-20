import hypothesis_testing as ht                                              

mu = 1.1
sigma = 10.0
epsilon = 1.0
n_throws = 50

ht.test_catapult(mu, sigma, epsilon, n_throws, plotting = True, plot_folder = 'hypothesis_testing_plots', plot_main_name = 'Catapult')


P = 0.48
epsilon = 0.49
n_tosses = 100

ht.compare_coins(P, epsilon, n_tosses, verbose = True, plotting = True, plot_folder = 'hypothesis_testing_plots', plot_main_name = 'Coins')
