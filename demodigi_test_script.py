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

print_results = True
plot_results = True

known_background_1 = dd.background("hates computers", dd.standard_transformations["subtractive normal deterioration"], dd.standard_transformations["subtractive normal deterioration"], 0.2)
known_background_2 = dd.background("kazoo band outside office", dd.standard_transformations["no effect"], dd.standard_transformations["subtractive normal deterioration"], 0.1)
known_backgrounds = [known_background_1, known_background_2]

unknown_background_1 = dd.background("secretly a ghost", dd.standard_transformations["subtractive normal deterioration"], dd.standard_transformations["subtractive normal deterioration"], 0.1)
unknown_backgrounds = [unknown_background_1]

testgroup = dd.participants(8000, dd.standard_distributions["normal"], known_backgrounds = known_backgrounds, unknown_backgrounds = unknown_backgrounds)

if print_results:
   testgroup.describe()


default = dd.standard_transformations["additive normal improvement (big)"]

manipulation_1 = dd.manipulation("funny hats", dd.standard_transformations["additive normal improvement"])
manipulation_2 = dd.manipulation("prayer and incense", dd.standard_transformations["additive normal improvement"])
manipulation_3 = dd.manipulation("all text in comic sans", dd.standard_transformations["no effect"])
manipulations = [manipulation_1, manipulation_2, manipulation_3]

bounds = dd.skill_boundaries(25, 50, minimum_quality_difference = 0.1)

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
