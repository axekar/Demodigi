"""
This is a script for testing that the module factorial_experiment
actually works as intended.
"""

import numpy as np

import factorial_experiment as fe

print('Testing ordinalise...')
already_ordinal = list(range(0, 5))
ordinalised = fe.ordinalise(already_ordinal)
stays_same = np.all(ordinalised == np.arange(0, 5))
reverse_data = list(reversed(range(0, 5)))
ordinalised = fe.ordinalise(reverse_data)
reverses = np.all(ordinalised == np.asarray(list(reversed(range(0, 5)))))

if not stays_same:
   print('Already ordinal data is reordered!')
if not reverses:
   print('Data in reverse order is not reversed')
if stays_same and reverses:
   print('ordinalise passed tests!')


print('Testing logB...')
logB_one_handling = np.exp(fe.logB(1, 1)) == 1
logB_symmetry = True
for alpha in range(1, 10):
   for beta in range(1, 10):
      logB_symmetry = logB_symmetry and fe.logB(alpha, beta) == fe.logB(beta, alpha)

if not logB_one_handling:
   print('logB does not handle ones correctly!')
if not logB_symmetry:
   print('logB is not symmetric!')
if logB_one_handling and logB_symmetry:
   print('logB passed tests!')
   
print('Testing methods of simulated_participant class...')
n_sessions = 13
n_skills = 7
test_participant = fe.simulated_participant('Alice')
test_participant.set_digicomp(0., 1.)
test_participant.calculate_results(n_sessions, n_skills)
always_fail = np.sum(test_participant.results[:,0]) == 0
always_succeed = np.sum(test_participant.results[:,n_sessions-1]) == n_skills
if not always_fail:
   print('Participant is succeeding even when her digital competence is zero!')
if not always_succeed:
   print('Participant is failing even when her digital competence is one!')
if always_fail and always_succeed:
   print('simulated_participant passed tests!')
   

