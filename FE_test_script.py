"""
This is a script for testing that the module factorial_experiment
actually works as intended.
"""

import numpy as np
import numpy.random as rd

import factorial_experiment as fe


# ordinalise

print('Testing ordinalise...')
already_ordinal = list(range(0, 5))
ordinalised = fe.ordinalise(already_ordinal)
stays_same = np.all(ordinalised == np.arange(0, 5))
reverse_data = list(reversed(range(0, 5)))
ordinalised = fe.ordinalise(reverse_data)
reverses = np.all(ordinalised == np.asarray(list(reversed(range(0, 5)))))
if not stays_same:
   print('Already ordered data is reordered!')
if not reverses:
   print('Data in reverse order is not reversed')
if stays_same and reverses:
   print('ordinalise passed tests!')


# logB

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


# simulated_manipulation

print('Testing simulated_manipulation class...')
test_manipulation = fe.simulated_manipulation('test', fe.standard_transformations['no effect'])
n_participants = 100
random_digicomp = rd.uniform(low=0.0, high=1.0, size=n_participants)
transformed = test_manipulation.transformation(random_digicomp)
transform_does_nothing = np.all(random_digicomp == transformed)
if not transform_does_nothing:
   print('Null transform still changes digital competence!')
if transform_does_nothing:
   print('simulated_manipulation passed tests!')


# simulated_CBV

print('Testing simulated_CBV class...')
null_transformation = lambda digicomp, cbv_value : digicomp
flat_PDF = lambda n : rd.uniform(low=18, high=65, size=n)
test_CBV = fe.simulated_CBV('test', null_transformation, null_transformation, flat_PDF)
n_participants = 100
random_digicomp = rd.uniform(low=0.0, high=1.0, size=n_participants)
pre_transform = test_CBV.pre_transformation(random_digicomp, test_CBV.PDF(n_participants))
post_transform = test_CBV.post_transformation(random_digicomp, test_CBV.PDF(n_participants))
pre_transform_does_nothing = np.all(random_digicomp == pre_transform)
post_transform_does_nothing = np.all(random_digicomp == post_transform)
if not pre_transform_does_nothing:
   print('Null pre-transform still changes digital competence!')
if not post_transform_does_nothing:
   print('Null post-transform still changes digital competence!')
if pre_transform_does_nothing and post_transform_does_nothing:
   print('simulated_CBV passed tests!')


# simulated_BBV

print('Testing simulated_BBV class...')
test_BBV = fe.simulated_BBV('test', fe.standard_transformations['no effect'], fe.standard_transformations['no effect'], 0.5)
n_participants = 100
random_digicomp = rd.uniform(low=0.0, high=1.0, size=n_participants)
pre_transform = test_BBV.pre_transformation(random_digicomp)
post_transform = test_BBV.post_transformation(random_digicomp)
pre_transform_does_nothing = np.all(random_digicomp == pre_transform)
post_transform_does_nothing = np.all(random_digicomp == post_transform)
if not pre_transform_does_nothing:
   print('Null pre-transform still changes digital competence!')
if not post_transform_does_nothing:
   print('Null post-transform still changes digital competence!')
if pre_transform_does_nothing and post_transform_does_nothing:
   print('simulated_BBV passed tests!')


# boundaries

print('Testing boundaries class...')
try:
   fe.boundaries(-0.1, 1.0, minimum_quality_difference = 0.)
   caught_too_low = False
except ValueError:
   caught_too_low = True
try:
   fe.boundaries(0.0, 1.1, minimum_quality_difference = 0.)
   caught_too_high = False
except ValueError:
   caught_too_high = True
try:
   fe.boundaries(1.0, 0.0, minimum_quality_difference = 0.)
   caught_transposed = False
except ValueError:
   caught_transposed = True
if not caught_too_low:
   print('boundaries class accepts lower boundary below zero!')
if not caught_too_high:
   print('boundaries class accepts upper boundary above one!')
if not caught_transposed:
   print('boundaries class accepts upper boundary lower than lower boundary!')
if caught_too_low and caught_too_high and caught_transposed:
   print('boundaries passed tests!')


# simulated_participant

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


# simulated_learning_module

print('Testing methods of simulated_learning_module class...')
n_sessions = 13
n_skills = 7
n_participants = 127
default_digicomp = 0
no_skill_no_effect = fe.simulated_learning_module(n_skills, n_sessions, n_participants, default_digicomp, fe.standard_transformations['no effect'])
no_skill_no_effect.run_simulation()
all_fail = np.sum(no_skill_no_effect.results[:,0]) == 0
default_digicomp = 1.0
full_skill_no_effect = fe.simulated_learning_module(n_skills, n_sessions, n_participants, default_digicomp, fe.standard_transformations['no effect'])
full_skill_no_effect.run_simulation()
all_succeed = np.all(full_skill_no_effect.results[:,0] == n_skills)
if not all_fail:
   print('Participants are succeeding even when their digital competence is zero!')
if not all_succeed:
   print('Participants are failing even when their digital competence is one!')
if all_fail and all_succeed:
   print('simulated_learning_module passed tests!')

