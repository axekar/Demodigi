"""
This is a script that uses the module differences to generate the plots
in the internal Demokratisk Digitalisering document "Statistisk analys
av kvalitetsskillnader".
"""

import differences as df

# Number of trials for plots exploring long-run behaviour
n_trials = 10000

# Whether to run long-run trial for normal experiment
big_plot = False

# Generate plots of a single experimental run with normally distributed
# variables
mu_A = 102
mu_B = 98
sigma = 10
n_throws = 20
df.compare_catapults(mu_A, mu_B, sigma, sigma, n_throws)

# Generate plots of a single experimental run with binomial variables
P_A = 0.6
P_B = 0.4
n_tosses = 20
df.compare_coins(P_A, P_B, n_tosses)

# Generate plot describing long-term behaviour of binomial experiment
df.coin_long_run(P_A, P_B, n_tosses, n_trials)

# Generate plot describing long-term behaviour of normal experiment
#
# N.B.: This one takes a *long* time to run, and sometimes causes my
#       computer to run out of memory
if big_plot:
   df.catapult_long_run(102, 98, 10, 10, 20, n_trials)
