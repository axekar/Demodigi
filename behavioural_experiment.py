"""
This module was written for the ESF-financed project Demokratisk
Digitalisering. The project is a collaboration between
Arbetsförmedlingen (AF) and Kungliga Tekniska Högskolan (KTH). The
purpose of the project is to increase the digital competence - as
defined at https://ec.europa.eu/jrc/en/digcomp - of people working at
Arbetsförmedlingen, and by extension also job seekers. This shall be
done by learning modules at KTH using OLI-Torus.

--- About the module ---

The module simulates the behavioural experiments that we intend to do
as part of the project. In the experiment, some participants will get
to take the teaching module at an early time, and others at a later
time. This creates a window where some have taken the module and others
have not. During this window we will put them in some kind of
experimental situation. What that is will vary from module to module,
but in some way they will get the opportunity to perform some kind of
desired behaviour, which the module is supposed to teach. We will then
try to determine if those who have taken the module are more inclined
towards that behaviour than those who have not yet done so.

We assume that participants are essentially weighted coins, whose
weighting differs depending on whether they have taken the teaching
module. We use the following notation:

 P_pre: The probability that a person who has not yet taken a teaching
        module will perform the desired behaviour.

 P_post: The probability that a person who has taken a teaching module
        will perform the desired behaviour.

One purpose of this is to allow us to estimate the minimum number of
test subjects that will allow us to show with some appreciable degree
of certainty that P_post is significantly larger than P_pre. This would
be useful to know, since the smaller a planned experiment is, the more
likely it is that we will get actually get permission to do it.

Written by Alvin Gavel

https://github.com/Alvin-Gavel/Demodigi
"""

import numpy as np
import scipy.special as sp
import numpy.random as rd
import matplotlib.pyplot as plt

### Magic numbers, will probably be incorporated into a class at some point

# When estimating the probability distribution p over some probability P,
# how many steps are used
_p_steps = 101
# Corresponding for the difference between two probabilities.
_d_steps = 2 * _p_steps - 1


### Assorted mathematical stuff

def logB(alpha, beta):
   """
   The logarithm of the normalisation factor that appears when doing
   Bayesian fitting of binomial functions.
   """
   return sp.loggamma(alpha) + sp.loggamma(beta) - sp.loggamma(alpha + beta)

### Generic probability-distributions stuff

def test_normalisation(p, sample_width):
   p_mass = p * sample_width
   total_mass = sum(p_mass)
   if np.abs(total_mass - 1) > 0.01:
      print("Problem in calculation!")
      print("Probability density function not well normalised")
      print("Total probability mass: {}".format(total_mass))
   return


### The actual experiment

def single_trial(n, P):
   """
   Make a single iteration of the experiment, with n participants, for a
   given value of P.
   """
   successes = np.sum(rd.random(n) < P)
   return successes

def estimate_P(n, successes):
   """
   Given the results of a single trial, estimates the probabilility P of
   success.

   Returns an array containing the probability distribution p over P.
   """
   p_sample_width = 1 / _p_steps
   P_range = np.linspace(0.0, 1.0, num=_p_steps)
   with np.errstate(divide = 'ignore'):
      log_p = successes * np.log(P_range) + (n - successes) * np.log(1 - P_range) - logB(successes + 1, n - successes + 1)
   p = np.exp(log_p)
   test_normalisation(p, p_sample_width)
   return P_range, p

def estimate_D(p_pre, p_post):
   """
   Given two distributions p_pre and p_post over success chances P_pre and
   P_post, calculates the probability distribution d over the difference D
   between p_pre and p_post.
   """
   D_range = np.linspace(-1.0, 1.0, num=_d_steps)
   d = np.convolve(p_post, np.flip(p_pre))
   return D_range, d

def estimate_pdpos(D_range, d, practical_significance = 0.0):
   """
   Given a probability distribution d over the difference in quality D,
   calculate the probability that D is positive.
   """
   return sum(d[_p_steps:]) / sum(d) # Kluge, fix tomorrow

def median_pdpos(n, P_pre, P_post, runs, practical_significance = 0.0):
   """
   Makes multiple iterations of the experiment, with n participants, for
   a given value of p, each time estimating the probability that d is
   positive.
   """
   estimates = []
   for i in range(runs):
      dummy, p_pre = estimate_P(n, single_trial(n, P_pre))
      dummy, p_post = estimate_P(n, single_trial(n, P_post))
      D_range, d = estimate_D(p_pre, p_post)
      pdpos = estimate_pdpos(D_range, d, practical_significance)
      estimates.append(pdpos)
   return np.median(estimates)

def range_pdpos(n_min, n_max, P_pre, P_post, runs):
   """
   Calculates pdpos for a range of values of n
   """
   medians = []
   n = np.arange(n_min, n_max)
   for i in n:
      medians.append(median_pdpos(i, P_pre, P_post, runs))
   return n, medians

def plot_pdpos(n, medians):
   plt.clf()
   plt.plot(n, medians)
   plt.xlabel(r"$n$")
   plt.ylabel(r"Median $P\left(D > 0 \right)$")
   plt.show()
   return
