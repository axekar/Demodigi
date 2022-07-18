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


### Functions for finding values in arrays

def find_nearest(array, value):
   """
   Function for locating the value in an array that is closest to a given
   value.
   
   Function by unutbu at StackOverflow:
   https://stackoverflow.com/questions/2566412/find-nearest-value-in-numpy-array
   """
   idx = (np.abs(array - value)).argmin()
   return idx
   

### Statistics functions

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
   
   P(p | n, k)
   """
   def B(alpha, beta):
      return sp.gamma(alpha) * sp.gamma(beta) / sp.gamma(alpha + beta)
   return p**k * (1-p)**(n-k) / B(k + 1, n - k + 1)


def bayesian_analysis(n, k, epsilon = 0.01, plot = False):
   def plot_posterior(p_vector, posterior_vector, plot_folder = 'coin_tossing_plots'):
      """
      Plot the posterior distribution P(p | n, k)
      """
      fig, axs = plt.subplots()
      axs.plot(p_vector, posterior_vector)
      axs.set(xlabel=r'$p$', ylabel=r'$P\left( p | n, k \right)$', title = r'$n = {}$, $k = {}$'.format(n, k))
      top = axs.get_ylim()[1]
      #axs.vlines(0.5, 0, top, linestyles = 'dashed', color = 'black')
      axs.set_xlim(0, 1)
      axs.set_ylim(0, top)
      fig.set_size_inches(12, 4)
      fig.tight_layout()
      plt.savefig('./{}/posterior.png'.format(plot_folder))
      plt.close()
      return

   n_steps = 1000
   p_vector = np.linspace(0, 1, n_steps)
   posterior_vector = posterior(p_vector, n, k)
   
   left_bound = 0.5 - epsilon
   left_index = find_nearest(p_vector, left_bound)
   right_bound = 0.5 + epsilon
   right_index = find_nearest(p_vector, right_bound)
   
   P_even = np.trapz(posterior_vector[left_index:right_index], x=p_vector[left_index:right_index])
   print('Probability that coin is even: {:.3f}'.format(P_even))
   
   if plot:
      plot_posterior(p_vector, posterior_vector)
   return
   
def frequentist_analysis(n, k, epsilon = 0.01, plot = False):
   def plot_likelihood_as_function_of_p(p_vector, likelihood_as_function_of_p, plot_folder = 'coin_tossing_plots'):
      """
      Plot the likelihood distribution P(k | n, p), as a function of p
      """
      fig, axs = plt.subplots()
      axs.plot(p_vector, likelihood_as_function_of_p)
      axs.set(xlabel=r'$p$', ylabel=r'$P\left( k | n, p \right)$', title = r'$n = {}$, $k = {}$'.format(n, k))
      top = axs.get_ylim()[1]
      #axs.vlines(0.5, 0, top, linestyles = 'dashed', color = 'black')
      axs.set_xlim(0, 1)
      axs.set_ylim(0, top)
      fig.set_size_inches(12, 4)
      fig.tight_layout()
      plt.savefig('./{}/likelihood_as_function_of_p.png'.format(plot_folder))
      plt.close()
      return
   
   def plot_likelihood_as_function_of_k(k_vector, likelihood_as_function_of_k, plot_folder = 'coin_tossing_plots'):
      """
      Plot the likelihood distribution P(k | n, p), as a function of k
      """
      fig, axs = plt.subplots()
      axs.plot(k_vector, likelihood_as_function_of_k)
      axs.set(xlabel=r'$k$', ylabel=r'$P\left( k | n, p \right)$', title = r'$n = {}$, $k = {}$'.format(n, k))
      top = axs.get_ylim()[1]
      #axs.vlines(0.5, 0, top, linestyles = 'dashed', color = 'black')
      axs.set_xlim(0, n)
      axs.set_ylim(0, top)
      fig.set_size_inches(12, 4)
      fig.tight_layout()
      plt.savefig('./{}/likelihood_as_function_of_k.png'.format(plot_folder))
      plt.close()
      return

   n_steps = 1000
   p_vector = np.linspace(0, 1, n_steps)
   likelihood_as_function_of_p = likelihood(n, k, p_vector)
   
   left_bound = 0.5 - epsilon
   left_index = find_nearest(p_vector, left_bound)
   right_bound = 0.5 + epsilon
   right_index = find_nearest(p_vector, right_bound)
   
   max_index = np.argmax(likelihood_as_function_of_p[left_index:right_index])
   p_hat = likelihood_as_function_of_p[left_index:right_index][max_index]
   
   print('Maximum-likelihood estimate of p: {:.2f}'.format(p_hat))
   
   k_vector = np.linspace(0, n, n_steps)
   likelihood_as_function_of_k = likelihood(n, k_vector, p_hat)
   
   extreme_index = find_nearest(k_vector, k)
   p_value = np.trapz(likelihood_as_function_of_k[extreme_index:], x=likelihood_as_function_of_k[extreme_index:])
   print('p-value of null hypothesis that coin is even: {:.3f}'.format(p_value))
   
   if plot:
      plot_likelihood_as_function_of_p(p_vector, likelihood_as_function_of_p)
      plot_likelihood_as_function_of_k(k_vector, likelihood_as_function_of_k)
   return
