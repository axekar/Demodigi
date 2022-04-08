"""
This is a script for testing the module demodigi, by running a
simulated study with 1000 participants and three manipulations, two of
which give a slight improvement and one of which does nothing. There
are three background variables that affect the initial digital
competence, the effect of the learning module, or both. Two of them are
known, and one is unknown.

Setting print_results to True gives a verbose description of the
results of the study.

Setting plot_results to True causes it to attempt to make plots in a
folder named DD_plots, which has to be in the same directory as the
script is run in.

Setting save_results to True causes it to save json files with the
simulated particpants' results in a folder named Simulated_results,
which has to be in the same directory as the script is run in.

setting load_results to True causes it to attempt to load the results
that were saved by save_results. This is mostly to allow quickly
testing that the loading and saving works.
"""

import factorial_experiment as fe

# Prints verbose output describing the simulated study
print_results = True

# Makes plots describing the simulated study
plot_results = True

# Output three files containing flags and results for the participants
save_results = True

# Test that loading the results works
load_results = True


# We introduce two known backgrounds, one which affects both initial
# skill and the effectiveness of the intervention, and one which affects
# only the effectiveness of the intervention.

known_background_1 = fe.simulated_background("hates computers", fe.standard_transformations["large deterioration"], fe.standard_transformations["slight deterioration"], 0.2)
known_background_2 = fe.simulated_background("kazoo band outside office", fe.standard_transformations["no effect"], fe.standard_transformations["slight deterioration"], 0.1)
known_backgrounds = [known_background_1, known_background_2]


# We introduce one unknown background, which affects both initial skill
# and the effectiveness of the intervention.

unknown_background_1 = fe.simulated_background("secretly a ghost", fe.standard_transformations["moderate deterioration"], fe.standard_transformations["slight deterioration"], 0.1)
unknown_backgrounds = [unknown_background_1]


# Define three manipulations, two of which have a slight effect and one
# of which does nothing.

manipulation_1 = fe.simulated_manipulation("funny hats", fe.standard_transformations["slight improvement"])
manipulation_2 = fe.simulated_manipulation("prayer and incense", fe.standard_transformations["slight improvement"])
manipulation_3 = fe.simulated_manipulation("all text in comic sans", fe.standard_transformations["no effect"])
manipulations = [manipulation_1, manipulation_2, manipulation_3]


# Define the bounds for what we consider to be good and poor digital
# competence. The study will then, among other things, test how many
# participants who are moved from poor to good competence. (This means
# that it does not simply look at how many are pushed from just below
# to just above the threshold for poor competence.

bounds = fe.boundaries(0.5, 0.75, minimum_quality_difference = 0.1)


# We define a test group of 8000 participants, who are assumed to start
# out with a digital competence of 0.5, meaning that they have a 50%
# chance of answering a question correctly.

# Number of summative questions given in the learning module
n_participants = 1000
n_skills = 40
n_sessions = 5

# Define the effect that the learning module has, in the absence of any
# manipulations
default = fe.standard_transformations["large improvement"]

testgroup = fe.simulated_learning_module(n_skills, n_sessions, n_participants, 0.5, default, known_backgrounds = known_backgrounds, unknown_backgrounds = unknown_backgrounds, boundaries = bounds)
testgroup.set_manipulations(manipulations)
if print_results:
   testgroup.describe()
testgroup.run_simulation()
if save_results:
   testgroup.save_ids('simulated_participants.json')
   testgroup.save_backgrounds('simulated_backgrounds.json')
   testgroup.save_manipulations('simulated_manipulations.json')
   testgroup.save_results('Simulated_results')

# Everything is put together into a study, which is then run and the
# desired output is displayed

trial_study = fe.study('test', testgroup)
if print_results:
   trial_study.describe()
trial_study.do_tests()
if print_results:
   trial_study.summarise_results()
if plot_results:
   trial_study.plot_folder = 'DD_plots'
   trial_study.plot_results()
   trial_study.plot_participants()


# The data that was just saved is loaded again

if load_results:
   print('Loading saved data...')
   loaded_learning_module = fe.real_learning_module(n_skills, n_sessions, 'simulated_participants.json', 'simulated_backgrounds.json', 'Simulated_results', boundaries = bounds)
   loaded_learning_module.load_manipulations('simulated_manipulations.json')
   loaded_study = fe.study('test of loading', loaded_learning_module)
   loaded_study.do_tests()
   if print_results:
      loaded_study.summarise_results()
