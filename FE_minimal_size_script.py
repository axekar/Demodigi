"""
This script is intended to help identify the minimum number of
participants necessary to tell the effects of two manipulations that we
actually intend to do
"""

import numpy as np
import matplotlib.pyplot as plt

import factorial_experiment as fe

# Makes plots describing the simulated study
plot_results = True


# First we simulate the minimum number of participants needed for us to
# tell that the learning modules do anything at all

absolute_minimum = fe.minimal_size_experiment('Absolute minimum', 0.5, fe.standard_transformations["minimal improvement"], 40, [], [], 10, 200, n_steps = 190, iterations = 100)
absolute_minimum.run()
if plot_results:
   absolute_minimum.plot_folder = 'DD_plots'
   absolute_minimum.plot()


age = fe.simulated_background("old enough to have grown up without PC", fe.standard_transformations["no effect"], fe.standard_transformations["no effect"], 0.25)
gender = fe.simulated_background("is a guy", fe.standard_transformations["no effect"], fe.standard_transformations["no effect"], 0.5)
motivated = fe.simulated_background("low motivation", fe.standard_transformations["no effect"], fe.standard_transformations["no effect"], 0.20)

QBL_PQBL = fe.simulated_manipulation("Pure Question-based Learning", fe.standard_transformations["minimal improvement"])
goals = fe.simulated_manipulation("Goal setting", fe.standard_transformations["minimal improvement"])

minimum = fe.minimal_size_experiment('Minimum', 0.5, fe.standard_transformations["minimal improvement"], 40, [QBL_PQBL, goals], [age, gender, motivated], 10, 200, n_steps = 190, iterations = 100)
minimum.run()
if plot_results:
   minimum.plot_folder = 'DD_plots'
   minimum.plot()
