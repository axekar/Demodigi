"""
This is a script for demonstrating how to use the module
factorial_experiment.

The scripts simulates study with 1000 participants and three
manipulations, two of which give a slight improvement and one of which
does nothing. There are three BBVs that affect the
initial digital competence, the effect of the learning module, or both.
Two of them are known, and one is unknown.

There are a couple of toggle which are by default set to True:

 - print_results gives a verbose description of the
results of the study.

 - plot_results causes the script to attempt to make plots in a
folder named DD_plots, which has to be in the same directory as the
script is run in.

 - save_results causes the script to save json files with the
simulated participants' results in a folder named Simulated_results,
which has to be in the same directory as the script is run in.

 - load_results causes the script to attempt to load the results
that were saved by save_results.
"""

import factorial_experiment as fe
import numpy.random as rd

# Prints verbose output describing the simulated study
print_results = True


# Makes plots describing the simulated study
plot_results = True


# Output three files containing flags and results for the participants
save_results = True


# Test that loading the results works
load_results = True


# We introduce two known BBVs, one which affects both initial skill and
# the effectiveness of the intervention, and one which affects only the
# effectiveness of the intervention.

known_BBV_1 = fe.simulated_BBV("hates computers", fe.standard_transformations["large deterioration"], fe.standard_transformations["slight deterioration"], 0.2)
known_BBV_2 = fe.simulated_BBV("office is bouncy castle", fe.standard_transformations["no effect"], fe.standard_transformations["slight deterioration"], 0.05)
known_BBVs = [known_BBV_1, known_BBV_2]


# We introduce one discovered BBV, which affects only the 
# the effectiveness of the intervention.

discovered_BBV = fe.simulated_BBV("kazoo band outside office", fe.standard_transformations["no effect"], fe.standard_transformations["slight deterioration"], 0.1)
discovered_BBVs = [discovered_BBV]


# We introduce one unknown BBV, which affects both initial skill
# and the effectiveness of the intervention.

unknown_BBV_1 = fe.simulated_BBV("secretly a ghost", fe.standard_transformations["moderate deterioration"], fe.standard_transformations["slight deterioration"], 0.1)
unknown_BBVs = [unknown_BBV_1]


# We introduce one CBV, which has no effect whatsoever

null_transformation = lambda digicomp, CBV_value : digicomp
CBV = fe.simulated_CBV("height", null_transformation, null_transformation, lambda n : rd.normal(loc=175., scale=8.0, size=n))
CBVs = [CBV]


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


# We define a test group of 1000 participants, who are assumed to start
# out with a digital competence of 0.5, meaning that they have a 50%
# chance of answering a question correctly. They are taught 40 different
# skills over the course of 5 sessions.
n_participants = 1000
n_skills = 40
n_sessions = 5
initial_digital_competence = 0.5


# Define the effect that the learning module has, in the absence of any
# manipulations
default_effect = fe.standard_transformations["large improvement"]

demo_group = fe.simulated_learning_module(n_skills, n_sessions, n_participants, initial_digital_competence, default_effect, known_BBVs = known_BBVs, discovered_BBVs = discovered_BBVs, unknown_BBVs = unknown_BBVs, CBVs = CBVs, boundaries = bounds)
demo_group.set_manipulations(manipulations)
if print_results:
   demo_group.describe()
demo_group.run_simulation()
if save_results:
   demo_group.save_ids('simulated_participants.json')
   demo_group.save_BBVs('simulated_BBVs.json')
   demo_group.save_manipulations('simulated_manipulations.json')
   demo_group.save_results('Simulated_results')


# Everything is put together into a study, which is then run and the
# desired output is displayed

trial_study = fe.study('Demonstration', demo_group)
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
   loaded_learning_module = fe.real_learning_module(n_skills, n_sessions, 'simulated_participants.json', 'simulated_BBVs.json', 'Simulated_results', boundaries = bounds)
   loaded_learning_module.load_manipulations('simulated_manipulations.json')
   loaded_study = fe.study('Demonstration of loading', loaded_learning_module)
   loaded_study.do_tests()
   if print_results:
      loaded_study.summarise_results()
