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
      axs.set(xlabel=r'$\Delta s$', ylabel=r'Antal', title = 'Kastlängder')
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

   # Plot histogram with overplotted best-fit
   if plotting:

      fig, axs = plt.subplots(1)
      axs.hist(throws, bins = n_bins, label = r'Observerat')
      bin_width = (max(throws) - min(throws)) / n_bins
      
      max_index = np.argmax(p)
      wide_mu_vector = np.linspace(mu - zoom_width, mu + zoom_width, num = n_steps)
      best_fit = st.norm.pdf(wide_mu_vector, loc = mu_grid.flatten()[max_index], scale = sigma_grid.flatten()[max_index])    
      axs.plot(wide_mu_vector, best_fit * n_throws * bin_width, label = r'Förväntat')

      axs.set_xlim(left = mu - zoom_width, right = mu + zoom_width)
     # axs.set_ylim(bottom = 0, top = histogram_y_max*1.1)
      axs.set(xlabel=r'$\Delta s$', ylabel=r'Antal kast', title = r'Bästa anpassning')
      axs.legend()
      fig.set_size_inches(12, 4)
      fig.tight_layout()
      plt.savefig('./{}/{}_best_fit.png'.format(plot_folder, plot_main_name))
      plt.close()

   ### Frequentist analysis
   
   # Maximum-likelihood estimation, within the bounds

   return


### Everything below here will be absorbed into a test_coin function ###
def compare_coins(P, epsilon, n_tosses, verbose = True, plotting = True, plot_folder = 'hypothesis_testing_plots', plot_main_name = 'Coins'):
   def logB(alpha, beta):
      """
      The logarithm of the normalisation factor to the binomial likelihood
      """
      return sp.loggamma(alpha) + sp.loggamma(beta) - sp.loggamma(alpha + beta)

   if P > 1:
      print('Probabilities cannot be larger than one!')
      print('Value input was {}'.format(P))
      return
   if P < 0:
      print('Probabilities cannot be smaller than zero!')
      print('Value input was {}'.format(P))
      return

   heads = np.sum(rd.uniform(0., 1., size = n_tosses) < P)
   if verbose:
      print('Scored {} heads'.format(heads))
      
   # Make a vector of the possible values of P
   n_steps = 1000
   P_vector = np.linspace(0., 1., num = n_steps)

   # Calculate the log-likelihood
   
   # The log-likelihood P(successes|P)
   tails = n_tosses - heads
   with np.errstate(all = 'ignore'):
      log_L = heads * np.log(P_vector) + tails * np.log(1 - P_vector) - logB(heads + 1, tails + 1)
      if heads > 0:
         log_L[0] = - np.inf
      else:
         log_L[0] = - logB(heads + 1, tails + 1)
      if tails > 0:
         log_L[-1] = - np.inf
      else:
         log_L[-1] = - logB(heads + 1, tails + 1)

   L = np.exp(log_L)
   maxL = np.max(L)

   if plotting:
      fig, axs = plt.subplots(1)
      axs.plot(P_vector, L)
      axs.vlines(P, 0, maxL * 1.1, linestyles = 'dashed')
      axs.set_xlim(left = 0, right = 1)
      axs.set_ylim(bottom = 0, top = maxL * 1.1)
      axs.set(xlabel=r'$P$', ylabel=r'$L\left( P \right)$', title = r'$p(kast|P)$')
      fig.set_size_inches(12, 4)
      fig.tight_layout()
      plt.savefig('./{}/{}_likelihood.png'.format(plot_folder, plot_main_name))
      plt.close()
      
   ### Bayesian analysis
   
   log_prior = np.zeros(n_steps)
   log_pP = log_prior + log_L
   pP = np.exp(log_pP)
   max_pP = np.max(pP)

   left_epsilon_index = np.searchsorted(P_vector, -epsilon, side='left')
   right_epsilon_index = np.searchsorted(P_vector, epsilon, side='left')

   P_between = np.sum(pP[left_epsilon_index:right_epsilon_index]) / np.sum(pP)

   if plotting:
      fig, axs = plt.subplots(1)
      axs.plot(P_vector, pP)
      
      axs.fill_between(P_vector[left_epsilon_index:right_epsilon_index], pP[left_epsilon_index:right_epsilon_index])      
      
      P_index = np.searchsorted(P_vector, P, side='left')
      if left_epsilon_index < P_index < right_epsilon_index:
         axs.vlines(P, 0, pP[P_index], linestyles = 'dashed', colors = 'white')
      else:
         axs.vlines(P, 0, pP[P_index], linestyles = 'dashed')
      axs.vlines(P, pP[P_index], max_pP * 1.1, linestyles = 'dashed')

      axs.set_xlim(left = 0, right = 1)
      axs.set_ylim(bottom = 0, top = max_pP * 1.1)
      axs.set(xlabel=r'$P$', ylabel=r'$p\left( P | kast \right)$', title = r'Bayesiansk posterior')
      fig.set_size_inches(12, 4)
      fig.tight_layout()
      plt.savefig('./{}/{}_posterior.png'.format(plot_folder, plot_main_name))
      plt.close()

   return
