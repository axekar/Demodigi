"""
This script was written for the ESF-financed project Demokratisk
Digitalisering. The project is a collaboration between
Arbetsförmedlingen (AF) and Kungliga Tekniska Högskolan (KTH). The
purpose of the project is to increase the digital competence - as
defined at https://ec.europa.eu/jrc/en/digcomp - of people working at
Arbetsförmedlingen and by extension also job seekers. This will be
done by learning modules at KTH using OLI-Torus.

--- About this Python module ---

This module demonstrates how a Bayesian and a frequentist might
tackle the question of whether a coin is weighted.

Written by Alvin Gavel
https://github.com/Alvin-Gavel/Demodigi
"""

import numpy as np
import numpy.random as rd
import scipy.special as sp
import matplotlib.pyplot as plt

# This ensured that the results will be the same from one run to the
# next. Turn this on when making plots for the document, and off if
# you want to play around with the model in a more realistic way.
rd.seed(1729)


def toss(n, p):
   """
   Take a coin with weight p and toss it n times.
   """
   return np.sum(rd.rand(n) < p)
   
   
def likelihood(n, k, p):
   """
   The likelihood of getting k successes after n trials given a success
   probability p
   
   P(k | n, p)
   """
   return sp.binom(n, k)* p**k * (1-p)**(n-k)
   
def posterior(p, n, k):
   """
   The posterior probability over p after observing k successes in n trials,
   assuming a flat prior over p.
   """
   def B(alpha, beta):
      return sp.gamma(alpha) * sp.gamma(beta) / sp.loggamma(alpha + beta)
   return p**k * (1-p)**(n-k) / B(1 + k, 1 + n - k)
   
