import coin_tossing as ct                                               

n = 10
p = 0.4
k = ct.toss(n, p)

ct.bayesian_analysis(n, k, plot=True)
