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


def compare_catapults(mu_A, mu_B, sigma_A, sigma_B, n_throws):
   """
   Say that we have two catapults A and B, and we want to know which one
   is better. We have decided that for our purposes the 'better' catapult
   is the one that one average throws rocks the furthest. We also believe
   that the range of the individual throws follows a normal distribution.
   """

   # Generate throws for each catapult   
   throws_A = sigma_A * rd.randn(n_throws) + mu_A
   throws_B = sigma_B * rd.randn(n_throws) + mu_B

   # A negative value for mu is not strictly *wrong*, but in practise the
   # range of a catapult is positive.
   mu_A = abs(mu_A)
   mu_B = abs(mu_B)
   
   # Make a grid of the possible values of mu and sigma. This would be
   # computationally infeasible if we had many parameters, but with just
   # two we can get away with it.
   min_mu = 0
   max_mu = 2 * max(mu_A, mu_B)
   min_sigma = 0
   max_sigma = 2 * max(sigma_A, sigma_B)
   
   n_steps = 100

   mu_vector = np.linspace(min_mu, max_mu, num = n_steps)
   sigma_vector = np.linspace(min_sigma, max_sigma, num = n_steps)

   mu_grid, sigma_grid = np.meshgrid(mu_vector, sigma_vector)

   # The log-prior P(mu, sigma). To stay consistent with a frequentist analysis,
   # we use a flat prior.
   log_prior_A = np.zeros((n_steps, n_steps))
   log_prior_B = np.zeros((n_steps, n_steps))

   # The unnormalised log-likelihood P(throws|mu, sigma)
   log_L_A_by_throw = np.zeros((n_steps, n_steps, n_throws))
   log_L_B_by_throw = np.zeros((n_steps, n_steps, n_throws))
   for i in range(n_throws):
      log_L_A_by_throw[:,:,i] = np.log(1. / (sigma_grid * np.sqrt(2 * np.pi))) + ( - (1./2.) * ((throws_A[i] - mu_grid) / (sigma_grid))**2)
      log_L_B_by_throw[:,:,i] = np.log(1. / (sigma_grid * np.sqrt(2 * np.pi))) + ( - (1./2.) * ((throws_B[i] - mu_grid) / (sigma_grid))**2)
   log_L_A = np.sum(log_L_A_by_throw, axis = 2)
   log_L_B = np.sum(log_L_B_by_throw, axis = 2)
   
   # The unnormalised log-posterior
   log_P_A = log_prior_A + log_L_A
   log_P_B = log_prior_B + log_L_B
   
   fig, axs = plt.subplots(2)
   axs[0].pcolormesh(mu_grid, sigma_grid, np.exp(log_P_A))
   axs[1].pcolormesh(mu_grid, sigma_grid, np.exp(log_P_B))
   for ax in axs.flat:
      ax.set(xlabel=r'$\mu$', ylabel=r'$\sigma$')

   plt.show()
   return
