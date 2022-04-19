"""
This is a script for testing that the module factorial_experiment
actually works as intended.
"""

import numpy as np

import factorial_experiment as fe

print('Testing logB...')
logB_one_handling = np.exp(fe.logB(1, 1)) == 1
logB_symmetry = True
for alpha in range(1, 10):
   for beta in range(1, 10):
      logB_symmetry = logB_symmetry and fe.logB(alpha, beta) == fe.logB(beta, alpha)

if logB_one_handling:
   print('logB handles ones correctly')
else:
   print('logB does not handle ones correctly!')
if logB_symmetry:
   print('logB is symmetric')
else:
   print('logB is not symmetric!')
