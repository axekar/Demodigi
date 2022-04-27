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


# Our current best guesses about the numbers relevant to the study
default_digicomp = 0.5
default_effect = fe.standard_transformations["minimal improvement"]
n_skills = 30
n_sessions = 4


# First we simulate the minimum number of participants needed for us to
# tell that the learning modules do anything at all

absolute_minimum = fe.minimal_size_experiment('Absolute minimum', default_digicomp, default_effect, n_skills, n_sessions, [], [], 10, 200, n_steps = 190, iterations = 100)
absolute_minimum.run()
if plot_results:
   absolute_minimum.plot_folder = 'DD_plots'
   absolute_minimum.plot()

# Define known binary background variables
age = fe.simulated_BBV("old enough to have grown up without PC", fe.standard_transformations["no effect"], fe.standard_transformations["no effect"], 0.25)
gender = fe.simulated_BBV("is a guy", fe.standard_transformations["no effect"], fe.standard_transformations["no effect"], 0.5)
motivated = fe.simulated_BBV("low motivation", fe.standard_transformations["no effect"], fe.standard_transformations["no effect"], 0.20)
known_BBVs = [age, gender, motivated]

# Define manipulations that we intend to test
QBL_PQBL = fe.simulated_manipulation("Pure Question-based Learning", fe.standard_transformations["minimal improvement"])
goals = fe.simulated_manipulation("Goal setting", fe.standard_transformations["minimal improvement"])
manipulations = [QBL_PQBL, goals]


# Run the test
minimum = fe.minimal_size_experiment('Minimum', default_digicomp, default_effect, n_skills, n_sessions, manipulations, known_BBVs, 10, 200, n_steps = 190, iterations = 100)
minimum.run()
if plot_results:
   minimum.plot_folder = 'DD_plots'
   minimum.plot()
