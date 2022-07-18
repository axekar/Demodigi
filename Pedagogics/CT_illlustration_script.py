import coin_tossing as ct                                               

n = 10
p = 0.4
k = ct.toss(n, p)
epsilon = 0.01

print('n: {}'.format(n))
print('k: {}'.format(k))

ct.bayesian_analysis(n, k, epsilon = epsilon, plot=True)
ct.frequentist_analysis(n, k, epsilon = epsilon, plot=True)
