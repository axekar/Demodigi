"""
This script is intended to help identify the minimum number of
participants necessary to tell the effects of two manipulations that we
actually intend to do
"""

import numpy as np
import matplotlib.pyplot as plt

import factorial_experiment as fe

group_sizes = [10, 20, 50, 100, 200, 500, 1000, 8000]
trials = range(10)


# First we try to find out the minimum group size that allow us to tell
# that the learning module has an effect, at all

median_results_before = []
median_results_after = []
median_median_test_results = []
for group_size in group_sizes:
   results_before = []
   results_after = []
   median_test_results = []
   for trial in trials:
      AF = fe.simulated_participants(group_size, 0.5, known_backgrounds = [], unknown_backgrounds = [], boundaries = None)
      minimal_study = fe.study('Minimal simulation', AF, 40)
      minimal_study.simulate_study(fe.standard_transformations["minimal improvement"])
      results_before.append(np.median(AF.results_pre))
      results_after.append(np.median(AF.results_post))
      minimal_study.do_tests()
      median_test_results.append(minimal_study.measured_results['median tests']['total']['after module']['probability that treatment group does better than control group'])
   median_results_before.append(np.median(results_before))
   median_results_after.append(np.median(results_after))
   median_median_test_results.append(np.median(median_test_results))

plt.clf()
plt.plot(group_sizes, median_median_test_results)
plt.show()


# Having done this, we try to find out the minimum group size that will
# allow us to tell that our manipulations have an effect

age = fe.simulated_background("old enough to have grown up without PC", fe.standard_transformations["no effect"], fe.standard_transformations["no effect"], 0.25)
gender = fe.simulated_background("Is a guy", fe.standard_transformations["no effect"], fe.standard_transformations["no effect"], 0.5)
motivated = fe.simulated_background("low motivation", fe.standard_transformations["no effect"], fe.standard_transformations["no effect"], 0.20)

QBL_PQBL = fe.simulated_manipulation("Pure Question-based Learning", fe.standard_transformations["minimal improvement"])
goals = fe.simulated_manipulation("Goal setting", fe.standard_transformations["minimal improvement"])

median_median_test_results = {'Pure Question-based Learning':[], 'Goal setting':[]}
for group_size in group_sizes:
   median_test_results = {}
   for manipulation_name in median_median_test_results.keys():
      median_test_results[manipulation_name] = []
      
   for trial in trials:
      AF = fe.simulated_participants(group_size, 0.5, known_backgrounds = [age, gender, motivated], unknown_backgrounds = [], boundaries = None)
      simulated_study = fe.study('Simulation looking at manipulations', AF, 40)
      simulated_study.set_manipulations([QBL_PQBL, goals])
   
      simulated_study.simulate_study(fe.standard_transformations["minimal improvement"])
      simulated_study.do_tests()
      for manipulation_name in median_median_test_results.keys():
          median_test_results[manipulation_name].append(simulated_study.measured_results['median tests'][manipulation_name]['after module']['probability that treatment group does better than control group'])
          
   for manipulation_name in median_median_test_results.keys():
      median_median_test_results[manipulation_name].append(np.median(median_test_results[manipulation_name]))

for manipulation_name in median_median_test_results.keys():
   plt.clf()
   plt.plot(group_sizes, median_median_test_results[manipulation_name])
   plt.title(manipulation_name)
   plt.show()
