import hypothesis_testing as ht                                              

n = 10
p = 0.4
k = ht.toss(n, p)
epsilon = 0.01

print('n: {}'.format(n))
print('k: {}'.format(k))

ht.bayesian_analysis(n, k, epsilon = epsilon, plot=True)
ht.frequentist_analysis(n, k, epsilon = epsilon, plot=True)
