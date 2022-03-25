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

import numbers as nb

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
   
   Attributes
   ----------
   name : str
   \tThe name of the experiment run
   plot_folder : str
   \tPath to a folder where plots should be run. If none is specified,
   \tplots are shown immediately instead.
   n_pre : int
   \tThe number of participants who have not yet taken the learning module
   n_post : int
   \tThe number of participants who have taken the learning module
   P_pre : float
   \tThe probability that a participant who has not taken the learning
   \tmodule will perform the desired behaviour
   P_post : float
   \tThe probability that a participant who has taken the learning module
   \twill perform the desired behaviour
   D : float
   \tThe difference P_post - P_pre
   S_pre : float
   \tThe number of those participants who have not taken the learning
   \twho still ended up performing the desired behaviour
   S_post : float
   \tThe number of those participants who have taken the learning module
   \twho end up performing the desired behaviour
   P_range : float ndarray
   \tThe range of values of P for which the probability distribution p(P)
   \tis calculated
   p_pre : float ndarray
   \tThe probability distribution p(P) for the participants who have not
   \tyet taken the learning module
   p_post : float ndarray
   \tThe probability distribution p(P) for the participants who have taken
   \tthe learning module
   D_range : float ndarray
   \tThe range of values of D for which the probability distribution d(D)
   \tis calculated
   d : float ndarray
   \tThe probability distribution d(D)
   pDpos : float
   \tThe probability that D is positive, based on d(D)
   """
   def __init__(self, n_pre, n_post, P_pre, P_post, name = ''):
      """
      Parameters
      ----------
      n_pre : int
      \tDescribed under attributes
      n_post : int
      \tDescribed under attributes
      P_pre : float
      \tDescribed under attributes
      P_post : float
      \tDescribed under attributes
      
      Optional parameters
      -------------------
      name : str
      \tDescribed under attributes
      """
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
      
      if name == '':
         self.name = '{}-{}_{}-{}'.format(self.n_pre, self.n_post, self.P_pre, self.P_post)
      else:
         self.name = name
      self.plot_folder = ''
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
      """
      Plot the probability distributions p(P) for the two participant groups
      """
      plt.clf()
      self._plot_with_dot(self.P_range, self.p_pre, 'pre', self.P_pre)
      self._plot_with_dot(self.P_range, self.p_post, 'post', self.P_post)
      plt.xlim(0, 1)
      plt.xlabel(r"$P$")
      plt.ylabel(r"$p\left( P \right)$")
      plt.xticks(ticks=np.linspace(0, 1, 11, endpoint=True))
      plt.legend()
      if self.plot_folder == '':
         plt.show()
      else:
         plt.savefig('./{}/ill_{}_p.png'.format(self.plot_folder, self.name))
      return
   
   def plot_d(self):
      """
      Plot the probability distribution d(D) for the participants
      """
      plt.clf()
      self._plot_with_dot(self.D_range, self.d, 'diff', 0.0)
      plt.fill_between(self.D_range, self.d, where = self.D_range > 0, step="mid", alpha=0.4)
      plt.xlim(-1, 1)
      plt.title(r"$P\left( D > 0 \right) = {:.2f}$".format(self.pDpos))
      plt.xlabel(r"$D$")
      plt.ylabel(r"$d\left( D \right)$")
      plt.xticks(ticks=np.linspace(-1, 1, 21, endpoint=True), rotation = 90)
      if self.plot_folder == '':
         plt.show()
      else:
         plt.savefig('./{}/ill_{}_d.png'.format(self.plot_folder, self.name))
      return

class varying_n:
   """
   This is intended to estimate for which numbers of participants, and for
   which P_pre and P_post, the study can be expected to get any useful
   results. It does this by running a large number of simulated experiment
   runs, and for each value of n taking the median of their estimated

   Optionally, it is possible to also include multiple values of P_pre and
   P_post
   
   Attributes
   ----------
   name : str
   \tThe name of the object. Used when saving data
   plot_folder : str
   \tPath to a folder where plots should be run. If none is specified,
   \tplots are shown immediately instead.
   n_min : int
   \tThe smallest number of participants n to look at
   n_max : int
   \tThe largest number of participants n to look at
   n_steps : int
   \tThe number of different values of n to simulate
   P_pre : float or list of float
   \tThe probability that a participant who has not taken the learning
   \tmodule will exhibit the desired behaviour
   P_post : float or list of float
   \tThe probability that a participant who has taken the learning
   \tmodule will exhibit the desired behaviour
   P_type : str
   \tWhether one or more values of each of P_pre and P_post are used
   P_steps : int
   \tHow many values of each of P_pre and P_post are used
   iterations : int
   \tThe number of experiment_runs to generate for each combination of n,
   \tP_pre and P_post
   ns : float ndarray
   \tArray of the different values of n to test
   median_pDpos : float ndarray
   \tArray of the medians of pDpos for the different combinations of n,
   \tP_pre and P_post
   """
   def __init__(self, n_min, n_max, P_pre, P_post, n_steps = 100, iterations = 100, name = ''):
      """
      Parameters
      ----------
      n_min : int
      \tDescribed under attributes
      n_max : int
      \tDescribed under attributes
      P_pre : float
      \tDescribed under attributes
      P_post : float
      \tDescribed under attributes
      
      Optional parameters
      -------------------
      name : str
      \tDescribed under attributes
      n_steps : int
      \tDescribed under attributes
      iterations : int
      \tDescribed under attributes
      """
      self.n_min = n_min
      self.n_max = n_max
      self.n_steps = n_steps

      self.iterations = iterations
      
      if isinstance(P_pre, nb.Number) and isinstance(P_post, nb.Number):
         self.P_pre = [P_pre]
         self.P_post = [P_post]
         self.P_type = 'single P'
         self.P_steps = 1
      elif isinstance(P_pre, list) and isinstance(P_post, list):
         if len(P_pre) == len(P_post):
            self.P_pre = P_pre
            self.P_post = P_post
            self.P_type = 'multiple P'
            self.P_steps = len(P_pre)
         else:
            print('P_pre has length {} but P_post has length {}'.format(len(P_pre), len(P_post)))
            return
      else:
         print('Cannot use P_pre and P_post of types {} and {}'.format(type(P_pre), type(P_post)))
         return

      self.ns = np.linspace(self.n_min, self.n_max, num = self.n_steps, endpoint = True, dtype = np.int64)
      self.median_pDpos = np.zeros((self.n_steps, self.P_steps), np.float64) * np.nan
      
      if name == '':
         if self.P_type == 'single P':
            self.name = '{}-{}_{}-{}'.format(self.n_min, self.n_max, P_pre, P_post)
         elif self.P_type == 'multiple P':
            self.name = '{}-{}_multi_P'.format(self.n_min, self.n_max)
      else:
         self.name = name
      self.plot_folder = ''
      return
   
   def run(self):
      """
      Start simulating experiment runs
      """
      for i in range(self.n_steps):
         n = self.ns[i]
         for j in range(self.P_steps):
            pDpos = []
            for k in range(self.iterations):
               run = experiment_run(n // 2, n // 2, self.P_pre[j], self.P_post[j])
               pDpos.append(run.pDpos)
            self.median_pDpos[i, j] = np.nanmedian(pDpos)
      return
      
   def plot_pDpos(self):
      """
      Plot median pDpos as a function of n
      """
      plt.clf()
      for m in range(self.P_steps):
         plt.plot(self.ns, self.median_pDpos[:,m], label = r'$P_{{\mathrm{{pre}}}} = {}, P_{{\mathrm{{post}}}} = {}$'.format(self.P_pre[m], self.P_post[m]))
      plt.xlabel(r"$n$")
      plt.ylabel(r"$P\left( D > 0 \right)$")
      plt.xlim(self.n_min, self.n_max)
      plt.legend()
      if self.plot_folder == '':
         plt.show()
      else:
         plt.savefig('./{}/ill_{}_pDpos.png'.format(self.plot_folder, self.name))
      return
