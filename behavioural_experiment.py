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
_D_sample_width = 1/ _d_steps

def _index_of_nearest(array, value):
   """
   Thanks to unutbu of Stackoverflow:
   https://stackoverflow.com/questions/2566412/find-nearest-value-in-numpy-array
   """
   array = np.asarray(array)
   idx = (np.abs(array - value)).argmin()
   return idx

### Statistical analysis

def logB(alpha, beta):
   """
   The logarithm of the normalisation factor that appears when doing
   Bayesian fitting of binomial functions.
   """
   return sp.loggamma(alpha) + sp.loggamma(beta) - sp.loggamma(alpha + beta)

def test_normalisation(p, sample_width):
   p_mass = p * sample_width
   total_mass = sum(p_mass)
   if np.abs(total_mass - 1) > 0.01:
      print("Problem in calculation!")
      print("Probability density function not well normalised")
      print("Total probability mass: {}".format(total_mass))
   return

def binomial_trial(n, P):
   """
   Make a single iteration of the experiment, with n participants, for a
   given value of P.
   """
   return np.sum(rd.random(n) < P)

def calculate_p(n, S):
   """
   Given the results of a single trial, estimates what the probability
   P of success actually was.

   Returns an array containing the probability distribution p over P.
   """
   p_sample_width = 1 / _p_steps
   P_range = np.linspace(0.0, 1.0, num=_p_steps)
   with np.errstate(divide = 'ignore'):
      log_p = S * np.log(P_range) + (n - S) * np.log(1 - P_range) - logB(S + 1, n - S + 1)
   p = np.exp(log_p)

   p /= np.trapz(p, dx=p_sample_width)
   return P_range, p

def calculate_d(p_pre, p_post):
   """
   Given two distributions p_pre and p_post over success chances P_pre and
   P_post, calculates the probability distribution d over the difference D
   between p_pre and p_post.
   """
   D_range = np.linspace(-1.0, 1.0, num=_d_steps)
   d = np.convolve(p_post, np.flip(p_pre))
   d /= np.trapz(d, dx=_D_sample_width)
   return D_range, d

def estimate_pDpos(D_range, d):
   """
   Given a probability distribution d over the difference in quality D,
   calculate the probability that D is positive.
   """
   zero_diff = _index_of_nearest(D_range, 0)
   return np.trapz(d[zero_diff:], dx = _D_sample_width)

### The actual experiment

class experiment_run:
   """
   This represents a single run of the experiment
   """
   def __init__(self, n_pre, n_post, P_pre, P_post):
      self.n_pre = n_pre
      self.n_post = n_post
      self.P_pre = P_pre
      self.P_post = P_post
      self.D = self.P_post - self.P_pre
      
      self.S_pre = binomial_trial(self.n_pre, self.P_pre)
      self.S_post = binomial_trial(self.n_post, self.P_post)
      
      self.P_range, self.p_pre = calculate_p(self.n_pre, self.S_pre)
      dummy, self.p_post = calculate_p(self.n_post, self.S_post)
      self.D_range, self.d = calculate_d(self.p_pre, self.p_post)
      self.pDpos = estimate_pDpos(self.D_range, self.d)
      return
      
   def _plot_with_dot(self, x_range, y_range, label, x_mark):
      """
      Plot the function f(x), with a dot located on the curve at some
      specific value of x.
      """
      plt.plot(x_range, y_range, label = label)
      y_mark = y_range[_index_of_nearest(x_range, x_mark)]
      plt.scatter(x_mark, y_mark, s = 10)
      return
      
   def plot_p(self):
      plt.clf()
      self._plot_with_dot(self.P_range, self.p_pre, 'pre', self.P_pre)
      self._plot_with_dot(self.P_range, self.p_post, 'post', self.P_post)
      plt.xlabel(r"$P$")
      plt.ylabel(r"$p\left( P \right)$")
      plt.legend()
      plt.show()
      return
   
   def plot_d(self):
      plt.clf()
      self._plot_with_dot(self.D_range, self.d, 'diff', 0.0)
      plt.fill_between(self.D_range, self.d, where = self.D_range > 0, step="mid", alpha=0.4)
      plt.title(r"$P\left( D > 0 \right) = {:.2f}$".format(self.pDpos))
      plt.xlabel(r"$D$")
      plt.ylabel(r"$d\left( D \right)$")
      plt.show()
      return



