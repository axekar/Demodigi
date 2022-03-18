"""
This is a script for testing the module demodigi, by running a
simulated study with 8000 participants and three manipulations, two of
which give a slight improvement and one of which does nothing. There
are three background variables that affect the initial digital
competence, the effect of the learning module, or both. Two of them are
known, and one is unknown.

Setting the variable print_results to true gives a verbose description
of the results of the study. Setting the variable plot_results to true
causes it to attempt to make plots in a folder named DD_plots, which
has to be in the same directory as the script is run in.
"""

import demodigi as dd

# Prints verbose output describing the simulated study
print_results = True
# Makes plots describing the simulated study
plot_results = True


# We introduce two known backgrounds, one which affects both initial
# skill and the effectiveness of the intervention, and one which affects
# only the effectiveness of the intervention.

known_background_1 = dd.simulated_background("hates computers", dd.standard_transformations["subtractive normal deterioration"], dd.standard_transformations["subtractive normal deterioration"], 0.2)
known_background_2 = dd.simulated_background("kazoo band outside office", dd.standard_transformations["no effect"], dd.standard_transformations["subtractive normal deterioration"], 0.1)
known_backgrounds = [known_background_1, known_background_2]


# We introduce one unknown background, which affects both initial skill
# and the effectiveness of the intervention.

unknown_background_1 = dd.simulated_background("secretly a ghost", dd.standard_transformations["subtractive normal deterioration"], dd.standard_transformations["subtractive normal deterioration"], 0.1)
unknown_backgrounds = [unknown_background_1]


# We define a test group of 8000 participants, who are assumed to have
# skills following a normal distribution. (Note that this is not
# visible to the simulated experimentalists. They only have access to
# ordinal data).

testgroup = dd.participants(8000, dd.standard_distributions["normal"], known_backgrounds = known_backgrounds, unknown_backgrounds = unknown_backgrounds)
if print_results:
   testgroup.describe()


# Define the effect that the teaching module has, in the absence of any
# manipulations

default = dd.standard_transformations["additive normal improvement (big)"]


# Define three manipulations, two of which has a slight effect and one
# of which does nothing.

manipulation_1 = dd.simulated_manipulation("funny hats", dd.standard_transformations["additive normal improvement"])
manipulation_2 = dd.simulated_manipulation("prayer and incense", dd.standard_transformations["additive normal improvement"])
manipulation_3 = dd.simulated_manipulation("all text in comic sans", dd.standard_transformations["no effect"])
manipulations = [manipulation_1, manipulation_2, manipulation_3]


# Define the bounds for what we consider to be good and poor digital
# competence. The study will then, among other things, test how many
# participants who are moved from poor to good competence. (This means
# that it does not simply look at how many are pushed from just below
# to just above the threshold for poor competence.
bounds = dd.skill_boundaries(25, 50, minimum_quality_difference = 0.1)


# Everything is put together into a study, which is then run and the
# desired output is displayed
trial_study = dd.study('test', testgroup, default, manipulations, bounds = bounds)
if print_results:
   trial_study.describe()
trial_study.run_study()
if print_results:
   trial_study.summarise_results()
if plot_results:
   trial_study.plot_folder = 'DD_plots'
   trial_study.plot_results()
   trial_study.plot_participants()
