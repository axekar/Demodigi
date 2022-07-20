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

Note that the code is partly based on that in the differences module

Written by Alvin Gavel
https://github.com/Alvin-Gavel/Demodigi
"""

import numpy as np
import numpy.random as rd
import scipy.stats as st
import scipy.special as sp
import matplotlib.pyplot as plt



### Convenient functions

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

def test_catapult(mu, sigma, epsilon, n_throws, plotting = True, plot_folder = 'hypothesis_testing_plots', plot_main_name = 'Catapult'):
   
   ### Generate data
   
   throws = sigma * rd.randn(n_throws) + mu

   # This is my best guess for a sensible number of bins in a histogram
   n_bins = int(np.floor(np.sqrt(n_throws)))

   if plotting:
      fig, axs = plt.subplots(1)
      zoom_width = 3 * sigma
      axs.hist(throws, bins = n_bins, label = r'Observerat')
      axs.set(xlabel=r'Kaststräcka', ylabel=r'Antal')
      axs.set_xlim(left = mu - zoom_width, right = mu + zoom_width)
      fig.set_size_inches(12, 4)
      fig.tight_layout()
      plt.savefig('./{}/{}_histogram.png'.format(plot_folder, plot_main_name))
      plt.close()

   ### Calculate likelihood

   # Grid of possible mu and sigma
   n_steps = 1000
   delta_steps = 2 * n_steps - 1

   min_sigma = 0      
   min_mu = - 3 * sigma / np.sqrt(n_throws)
   max_sigma = 2 * sigma
   max_mu = 3 * sigma / np.sqrt(n_throws)

   mu_step_width = (max_mu - min_mu) / n_steps
   sigma_step_width = (max_sigma - min_sigma) / n_steps
   
   mu_vector = np.linspace(min_mu, max_mu, num = n_steps)
   sigma_vector = np.flip(np.linspace(max_sigma, min_sigma, num = n_steps, endpoint = False))
   mu_grid, sigma_grid = np.meshgrid(mu_vector, sigma_vector)

   # Calculate the log-likelihood
   log_L_by_throw = np.zeros((n_steps, n_steps, n_throws))
   for i in range(n_throws):
      log_L_by_throw[:,:,i] = np.log(1. / (sigma_grid * np.sqrt(2 * np.pi))) + ( - (1./2.) * ((throws[i] - mu_grid) / (sigma_grid))**2)
   log_L = np.sum(log_L_by_throw, axis = 2)
   L = np.exp(log_L)

   if plotting:
      fig, axs = plt.subplots(1)
      axs.pcolormesh(mu_grid, sigma_grid, L, shading = 'nearest')
      axs.scatter(mu, sigma, c = 'white', edgecolors = 'black')
      axs.vlines(-epsilon, min_sigma, max_sigma, colors = 'white', linestyles = 'dashed')
      axs.vlines(epsilon, min_sigma, max_sigma, colors = 'white', linestyles = 'dashed')
      axs.set(xlabel=r'$\mu$', ylabel=r'$\sigma$', title = r'Likelihood')     
      fig.set_size_inches(12, 4)
      fig.tight_layout()
      plt.savefig('./{}/{}_likelihood.png'.format(plot_folder, plot_main_name))
      plt.close()
      
   ### Bayesian analysis
   
   # Calculate posterior
   log_prior = np.zeros((n_steps, n_steps))
   log_p = log_prior + log_L
   p = np.exp(log_p)

   if plotting:
      fig, axs = plt.subplots(1)
      axs.pcolormesh(mu_grid, sigma_grid, p, shading = 'nearest')
      axs.scatter(mu, sigma, c = 'white', edgecolors = 'black')
      axs.vlines(-epsilon, min_sigma, max_sigma, colors = 'white', linestyles = 'dashed')
      axs.vlines(epsilon, min_sigma, max_sigma, colors = 'white', linestyles = 'dashed')
      axs.set(xlabel=r'$\mu$', ylabel=r'$\sigma$', title = r'Posterior')     
      fig.set_size_inches(12, 4)
      fig.tight_layout()
      plt.savefig('./{}/{}_posterior.png'.format(plot_folder, plot_main_name))
      plt.close()
   
   # The flattened posterior over mu and sigma   
   unnormalised_p_mu = np.sum(p, axis = 0)
   p_mu = unnormalised_p_mu / np.sum(unnormalised_p_mu * mu_step_width)
   max_p_mu = np.max(p_mu)     
   unnormalised_p_sigma = np.sum(p, axis = 1)
   p_sigma = unnormalised_p_sigma / np.sum(unnormalised_p_sigma * sigma_step_width)
   
   max_index = np.argmax(p)
   best_fit = st.norm.pdf(mu_vector, loc = mu_grid.flatten()[max_index], scale = sigma_grid.flatten()[max_index])

   left_epsilon_index = np.searchsorted(mu_vector, -epsilon, side='left')
   right_epsilon_index = np.searchsorted(mu_vector, epsilon, side='left')

   P_between = np.sum(p_sigma[left_epsilon_index:right_epsilon_index] * mu_step_width)
   
   if plotting:
      fig, axs = plt.subplots(1)
      axs.plot(mu_vector, p_mu)
      
      axs.fill_between(mu_vector[left_epsilon_index:right_epsilon_index], p_mu[left_epsilon_index:right_epsilon_index])      
      
      mu_index = np.searchsorted(mu_vector, mu, side='left')
      if left_epsilon_index < mu_index < right_epsilon_index:
         axs.vlines(mu, 0, p_mu[mu_index], linestyles = 'dashed', colors = 'white')
      else:
         axs.vlines(mu, 0, p_mu[mu_index], linestyles = 'dashed')
      axs.vlines(mu, p_mu[mu_index], max_p_mu * 1.1, linestyles = 'dashed')
      
      axs.set_xlim(left = min_mu, right = max_mu)
      axs.set_ylim(bottom = 0, top = max_p_mu * 1.1)
      axs.set(xlabel=r'$\mu$', ylabel=r'$p\left( \mu | kast \right)$', title = r'$P\left( kalib. \right) = {:.2f}$'.format(P_between))
      fig.set_size_inches(12, 4)
      fig.tight_layout()
      plt.savefig('./{}/{}_mu_posterior.png'.format(plot_folder, plot_main_name))
      plt.close()

   ### Frequentist analysis

   return


### Everything below here will be absorbed into a test_coin function ###

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
   def plot_posterior(p_vector, posterior_vector, plot_folder = 'hypothesis_testing_plots'):
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
   def plot_likelihood_as_function_of_p(p_vector, likelihood_as_function_of_p, plot_folder = 'hypothesis_testing_plots'):
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
   
   def plot_likelihood_as_function_of_k(k_vector, likelihood_as_function_of_k, plot_folder = 'hypothesis_testing_plots'):
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
   p_hat = p_vector[left_index:right_index][max_index]
   print('Maximum-likelihood estimate of p: {:.2f}'.format(p_hat))
      
   k_vector = np.arange(0, n + 1)
   k_exp = int(np.rint(p_hat * n))
   print('Expectation value of k: {}'.format(k_exp))

   delta_k = abs(k_exp - k)
   print('Discrepancy from expectation value: {}'.format(delta_k))
   
   likelihood_as_function_of_k = likelihood(n, k_vector, p_hat)
   p_value = (np.sum(likelihood_as_function_of_k[:k - delta_k]) + np.sum(likelihood_as_function_of_k[k + delta_k:])) / np.sum(likelihood_as_function_of_k)
   print('p-value: {:.2}'.format(p_value))
   
   if plot:
      plot_likelihood_as_function_of_p(p_vector, likelihood_as_function_of_p)
      plot_likelihood_as_function_of_k(k_vector, likelihood_as_function_of_k)
   return
