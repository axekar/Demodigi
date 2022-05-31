"""
This script was written for the ESF-financed project Demokratisk
Digitalisering. The project is a collaboration between
Arbetsförmedlingen (AF) and Kungliga Tekniska Högskolan (KTH). The
purpose of the project is to increase the digital competence - as
defined at https://ec.europa.eu/jrc/en/digcomp - of people working at
Arbetsförmedlingen and by extension also job seekers. This will be
done by learning modules at KTH using OLI-Torus.

--- About this Python script ---

This script is intended to demonstrate the idea behind looking at the
differences between two statistical distributions that describe the
estimated quality of two possible ways of implementing the learning
modules.

Written by Alvin Gavel
https://github.com/Alvin-Gavel/Demodigi
"""

import itertools

import numpy as np
import numpy.random as rd
import scipy.stats as st
import matplotlib.pyplot as plt


def compare_catapults(mu_A, mu_B, sigma_A, sigma_B, n_throws, plot_folder = 'differences_plots', plot_main_name = 'Catapults'):
   """
   Say that we have two catapults A and B, and we want to know which one
   is better. We have decided that for our purposes the 'better' catapult
   is the one that one average throws rocks the furthest. We also believe
   that the range of the individual throws follows a normal distribution.
   
   To figure out which one is best, we fire each catapult n times and put
   the results into our statistical model, which gives us a posterior
   probability over mu for each catapult. Using that we can calculate the
   probability distribution over the differences in mu. This then gives us
   the probability of one catapult being better than the other.
   """

   # If you for some reason want to adjust the code to look at more than
   # two catapults, the bit you need to modify starts here
   if sigma_A < 0 or sigma_B < 0:
      print('Standard deviation cannot be negative!')
      print('Values input were {} and {}'.format(sigma_A, sigma_B))
      return
   catapults = ['A', 'B']
   mu = {'A':abs(mu_A), 'B':abs(mu_B)}
   sigma = {'A':sigma_A, 'B':sigma_B}
   # Everything below here should be agnostic as to the number of catapults
   
   catapult_pairs = list(itertools.combinations(catapults, 2))

   # Generate throws for each catapult   
   throws = {}
   for catapult in catapults:
      throws[catapult] = sigma[catapult] * rd.randn(n_throws) + mu[catapult]

   # Make a grid of the possible values of mu and sigma. This would be
   # computationally infeasible if we had many parameters, but with just
   # two we can get away with it.
   n_steps = 1000
   delta_steps = 2 * n_steps - 1

   min_sigma = 0      
   min_mu = 0

   max_sigma = 0
   max_mu = 0
   for catapult in catapults:
      max_sigma = max(max_sigma, sigma[catapult])
      max_mu = max(max_mu, mu[catapult] + sigma[catapult])
   max_sigma = 2 * max_sigma
   max_mu = 2 * max_mu
   
   mu_step_width = (max_mu - min_mu) / n_steps

   mu_vector = np.linspace(min_mu, max_mu, num = n_steps)
   sigma_vector = np.flip(np.linspace(max_sigma, min_sigma, num = n_steps, endpoint = False))
   mu_grid, sigma_grid = np.meshgrid(mu_vector, sigma_vector)
   delta_vector = np.linspace(-max_mu, max_mu, num=delta_steps)

   # The log-prior P(mu, sigma). To stay consistent with a frequentist analysis,
   # we use a flat prior.
   log_prior = {}
   for catapult in catapults:
      log_prior[catapult] = np.zeros((n_steps, n_steps))

   # The unnormalised log-likelihood P(throws|mu, sigma)
   log_L_by_throw = {}
   log_L = {}
   for catapult in catapults:
      log_L_by_throw[catapult] = np.zeros((n_steps, n_steps, n_throws))
      for i in range(n_throws):
         log_L_by_throw[catapult][:,:,i] = np.log(1. / (sigma_grid * np.sqrt(2 * np.pi))) + ( - (1./2.) * ((throws[catapult][i] - mu_grid) / (sigma_grid))**2)
      log_L[catapult] = np.sum(log_L_by_throw[catapult], axis = 2)
   
   # The full posterior over mu and sigma
   log_P = {}
   P = {}
   for catapult in catapults:
      log_P[catapult] = log_prior[catapult] + log_L[catapult]
      P[catapult] = np.exp(log_P[catapult])
   
   fig, axs = plt.subplots(len(catapults))
   for i in range(len(catapults)):
      catapult = catapults[i]
      axs[i].pcolormesh(mu_grid, sigma_grid, P[catapult], shading = 'nearest')
      axs.flat[i].set(xlabel=r'$\mu$', ylabel=r'$\sigma$', title = 'Catapult {}'.format(catapult))
   fig.tight_layout()
   plt.savefig('./{}/{}_full_posteriors.png'.format(plot_folder, plot_main_name))
   plt.close()

   # The flattened posteriors over mu and sigma
   P_mu = {}
   P_sigma = {}
   best_fit = {}
   for catapult in catapults:
      P_mu[catapult] = np.sum(P[catapult], axis = 0)
      P_sigma[catapult] = np.sum(P[catapult], axis = 1)
      max_index = np.argmax(P[catapult])
      best_fit[catapult] = st.norm.pdf(mu_vector, loc = mu_grid.flatten()[max_index], scale = sigma_grid.flatten()[max_index])

   fig, axs = plt.subplots(len(catapults), 2)
   for i in range(len(catapults)):
      catapult = catapults[i]
      true_mu = mu[catapult]
      zoom_width = 3 * sigma[catapult]
      
      axs.flat[2*i].plot(mu_vector, P_mu[catapult] / np.max(P_mu[catapult]))
      axs.flat[2*i].vlines(true_mu, 0, 1)
      axs.flat[2*i].set_xlim(left = true_mu - zoom_width, right = true_mu + zoom_width)
      axs.flat[2*i].set(xlabel=r'$\mu$', ylabel=r'Unnorm. $P\left( \mu \right)$', title = 'Catapult {} posterior over $\mu$'.format(catapult))
      
      axs.flat[2*i+1].hist(throws[catapult], bins = n_throws // 5, label = 'Observed')
      axs.flat[2*i+1].plot(mu_vector, best_fit[catapult] * n_throws * 5, label = 'Expected')
      axs.flat[2*i+1].set_xlim(left = true_mu - zoom_width, right = true_mu + zoom_width)
      axs.flat[2*i+1].set(xlabel=r'$\mu$', ylabel=r'Throws', title = 'Catapult {} best fit posterior'.format(catapult))
      
   fig.tight_layout()
   plt.savefig('./{}/{}_mu_posteriors.png'.format(plot_folder, plot_main_name))
   plt.close()
   
   
   
   # The posterior over the differences in mu, and the probability that
   # the difference is below/above zero
   delta_mu = {}
   P_dle0 = {}
   P_dge0 = {}
   for catapult_pair in catapult_pairs:
      delta_mu[catapult_pair] = np.convolve(P_mu[catapult_pair[0]], np.flip(P_mu[catapult_pair[1]]))
      P_dle0[catapult_pair] = np.sum(delta_mu[catapult_pair][:n_steps]) / np.sum(delta_mu[catapult_pair])
      P_dge0[catapult_pair] = np.sum(delta_mu[catapult_pair][n_steps-1:]) / np.sum(delta_mu[catapult_pair])

   fig, axs = plt.subplots(len(catapult_pairs), 2)
   for i in range(len(catapult_pairs)):
      catapult_pair = catapult_pairs[i]
      true_delta = mu[catapult_pair[0]] - mu[catapult_pair[1]]
      zoom_width = 2 * max(sigma[catapult_pair[0]], sigma[catapult_pair[1]])
      normalised_delta_mu = delta_mu[catapult_pair] / np.max(delta_mu[catapult_pair])
      
      axs.flat[2*i].plot(delta_vector, normalised_delta_mu)
      axs.flat[2*i].vlines(true_delta, 0, 1)
      axs.flat[2*i].set(xlabel=r'$\Delta \mu$', ylabel=r'Unnorm. $P \left( \Delta \mu \right)$', title = 'Catapults {} & {} (full range)'.format(catapult_pair[0], catapult_pair[1]))
      
      axs.flat[2*i+1].plot(delta_vector, normalised_delta_mu)
      axs.flat[2*i+1].fill_between(delta_vector[n_steps-1:], normalised_delta_mu[n_steps-1:])
      axs.flat[2*i+1].set_xlim(left = true_delta - zoom_width, right = true_delta + zoom_width)
      axs.flat[2*i+1].set(xlabel=r'$\Delta \mu$', ylabel=r'Unnorm. $P \left( \Delta \mu \right)$', title = r'$P\left( \Delta \mu > 0 \right) = {:.2f}$'.format(P_dge0[catapult_pair]))
   fig.tight_layout()
   plt.savefig('./{}/{}_delta_posteriors.png'.format(plot_folder, plot_main_name))
   plt.close()

   return
