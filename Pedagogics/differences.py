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

import numpy as np
import numpy.random as rd
import matplotlib.pyplot as plt


def compare_catapults(mu_A, mu_B, sigma_A, sigma_B, n_throws, plot_folder = 'differences_plots', plot_main_name = 'Catapults'):
   """
   Say that we have two catapults A and B, and we want to know which one
   is better. We have decided that for our purposes the 'better' catapult
   is the one that one average throws rocks the furthest. We also believe
   that the range of the individual throws follows a normal distribution.
   """

   if sigma_A < 0 or sigma_B < 0:
      print('Standard deviation cannot be negative!')
      print('Values input were {} and {}'.format(sigma_A, sigma_B))
      return

   catapults = ['A', 'B']
   mu = {'A':abs(mu_A), 'B':abs(mu_B)}
   sigma = {'A':sigma_A, 'B':sigma_B}

   # Generate throws for each catapult   
   throws = {}
   for catapult in catapults:
      throws[catapult] = sigma[catapult] * rd.randn(n_throws) + mu[catapult]

   # Make a grid of the possible values of mu and sigma. This would be
   # computationally infeasible if we had many parameters, but with just
   # two we can get away with it.
   n_steps = 100
   
   min_mu = 0
   min_sigma = 0   

   max_mu = 0
   max_sigma = 0
   for catapult in catapults:
      max_mu = max(max_mu, mu[catapult])
      max_sigma = max(max_sigma, sigma[catapult])
   max_mu = 2 * max_mu
   max_sigma = 2 * max_sigma

   mu_vector = np.linspace(min_mu, max_mu, num = n_steps)
   sigma_vector = np.flip(np.linspace(max_sigma, min_sigma, num = n_steps, endpoint = False))
   mu_grid, sigma_grid = np.meshgrid(mu_vector, sigma_vector)

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
   
   # The posterior
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
   plt.savefig('./{}/{}_posteriors.png'.format(plot_folder, plot_main_name))

   return
