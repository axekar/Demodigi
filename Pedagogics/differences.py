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
import scipy.special as sp
import matplotlib.pyplot as plt


def compare_catapults(mu_A, mu_B, sigma_A, sigma_B, n_throws, plotting = True, plot_folder = 'differences_plots', plot_main_name = 'Catapults'):
   """
   Say that we have two catapults A and B, and we want to know which one
   is better. We have decided that for our purposes the 'better' catapult
   is the one that on average throws rocks the furthest. We also believe
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
   # A catapult with negative range isn't *wrong* per se, it just means
   # we have to turn it around before shooting
   mu = {'A':abs(mu_A), 'B':abs(mu_B)}
   sigma = {'A':sigma_A, 'B':sigma_B}
   # Everything below here should be agnostic as to the number of catapults
   
   catapult_pairs = list(itertools.combinations(catapults, 2))

   # I *think* scaling with the sqrt of the total number of counts makes
   # for the best histogram
   n_bins = int(np.floor(np.sqrt(n_throws)))

   # Generate throws for each catapult   
   throws = {}
   for catapult in catapults:
      throws[catapult] = sigma[catapult] * rd.randn(n_throws) + mu[catapult]

   # Start by making dummy histograms to figure out where the maxima end
   # up being
   fig, axs = plt.subplots(1, len(catapults))
   histogram_y_max = -np.inf
   for i in range(len(catapults)):   
      catapult = catapults[i]
      axs.flat[i].hist(throws[catapult], bins = n_bins)
      histogram_y_max = max(histogram_y_max, axs.flat[i].get_ylim()[1])
   plt.close()

   if plotting:
      fig, axs = plt.subplots(1, len(catapults))
      for i in range(len(catapults)):
         catapult = catapults[i]
         zoom_width = 3 * sigma[catapult]
         axs.flat[i].hist(throws[catapult], bins = n_bins, label = r'Observerat')
         axs.flat[i].set(xlabel=r'Kaststräcka', ylabel=r'Antal', title = r'Katapult {}'.format(catapult))
         axs.flat[i].set_xlim(left = mu[catapult] - zoom_width, right = mu[catapult] + zoom_width)
         axs.flat[i].set_ylim(bottom = 0, top = histogram_y_max*1.1)
      fig.set_size_inches(12, 4)
      fig.tight_layout()
      plt.savefig('./{}/{}_histogram.png'.format(plot_folder, plot_main_name))
      plt.close()

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
   
   mu_vector = np.linspace(min_mu, max_mu, num = n_steps)
   sigma_vector = np.flip(np.linspace(max_sigma, min_sigma, num = n_steps, endpoint = False))
   mu_grid, sigma_grid = np.meshgrid(mu_vector, sigma_vector)
   delta_vector = np.linspace(-max_mu, max_mu, num=delta_steps)

   mu_step_width = (max_mu - min_mu) / n_steps
   sigma_step_width = (max_sigma - min_sigma) / n_steps
   delta_step_width = (max(delta_vector) - min(delta_vector)) / delta_steps

   # To make the plots easy to compare, we will plot mu over the range of
   # the true mu:s plus-minus three times the biggest sigmas
   max_true_mu = -np.inf
   min_true_mu = np.inf
   max_true_sigma = 0
   for catapult in catapults:
      max_true_mu = max(max_true_mu, mu[catapult])
      min_true_mu = min(min_true_mu, mu[catapult])
      max_true_sigma = max(max_true_sigma, sigma[catapult])
   mu_plot_max = max_true_mu + 3 * max_true_sigma
   mu_plot_min = min_true_mu - 3 * max_true_sigma

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
   log_p = {}
   p = {}
   for catapult in catapults:
      log_p[catapult] = log_prior[catapult] + log_L[catapult]
      p[catapult] = np.exp(log_p[catapult])
   if plotting:
      fig, axs = plt.subplots(1, len(catapults))
      for i in range(len(catapults)):
         catapult = catapults[i]
         axs.flat[i].pcolormesh(mu_grid, sigma_grid, p[catapult], shading = 'nearest')
         for catapult_2 in catapults:
            if catapult_2 == catapult:
               c = 'white'
            else:
               c = 'grey'
            axs.flat[i].scatter(mu[catapult_2], sigma[catapult_2], c = c, edgecolors = 'black')
         axs.flat[i].set_xlim(left = mu_plot_min, right = mu_plot_max)
         axs.flat[i].set(xlabel=r'$\mu$', ylabel=r'$\sigma$', title = r'Katapult {}'.format(catapult))     
      fig.set_size_inches(12, 4)
      fig.tight_layout()
      plt.savefig('./{}/{}_full_posteriors.png'.format(plot_folder, plot_main_name))
      plt.close()

   # The flattened posteriors over mu and sigma
   p_mu = {}
   p_sigma = {}
   best_fit = {}
   max_p_mu = -np.inf
   for catapult in catapults:
      unnormalised_p_mu = np.sum(p[catapult], axis = 0)
      p_mu[catapult] = unnormalised_p_mu / np.sum(unnormalised_p_mu * mu_step_width)
      max_p_mu = max(max_p_mu, np.max(p_mu[catapult]))
      
      unnormalised_p_sigma = np.sum(p[catapult], axis = 1)
      p_sigma[catapult] = unnormalised_p_sigma / np.sum(unnormalised_p_sigma * sigma_step_width)
      max_index = np.argmax(p[catapult])
      best_fit[catapult] = st.norm.pdf(mu_vector, loc = mu_grid.flatten()[max_index], scale = sigma_grid.flatten()[max_index])

   if plotting:
      fig, axs = plt.subplots(1, len(catapults))
      for i in range(len(catapults)):
         catapult = catapults[i]
   
         axs.flat[i].plot(mu_vector, p_mu[catapult])
         for catapult_2 in catapults:
            true_mu = mu[catapult_2]
            if catapult_2 == catapult:
               linestyles = 'solid'
            else:
               linestyles = 'dashed'
            axs.flat[i].vlines(true_mu, 0, max_p_mu * 1.1, linestyles = linestyles)
         axs.flat[i].set_xlim(left = mu_plot_min, right = mu_plot_max)
         axs.flat[i].set_ylim(bottom = 0, top = max_p_mu * 1.1)
         axs.flat[i].set(xlabel=r'$\mu$', ylabel=r'$p\left( \mu \right)$', title = r'$p\left( \mu | kast \right)$ (katapult {})'.format(catapult))
      fig.set_size_inches(12, 4)
      fig.tight_layout()
      plt.savefig('./{}/{}_mu_posteriors.png'.format(plot_folder, plot_main_name))
      plt.close()

   if plotting:
      fig, axs = plt.subplots(1, len(catapults))
      for i in range(len(catapults)):
         catapult = catapults[i]
         true_mu = mu[catapult]
      
         axs.flat[i].hist(throws[catapult], bins = n_bins, label = r'Observerat')
         bin_width = (max(throws[catapult]) - min(throws[catapult])) / n_bins
         axs.flat[i].plot(mu_vector, best_fit[catapult] * n_throws * bin_width, label = r'Förväntat')
         axs.flat[i].set_xlim(left = mu_plot_min, right = mu_plot_max)
         axs.flat[i].set_ylim(bottom = 0, top = histogram_y_max*1.1)
         axs.flat[i].set(xlabel=r'Kastlängd', ylabel=r'Antal kast', title = r'Bästa anpassning (katapult {})'.format(catapult))
         axs.flat[i].legend()
      fig.set_size_inches(12, 4)
      fig.tight_layout()
      plt.savefig('./{}/{}_best_fit.png'.format(plot_folder, plot_main_name))
      plt.close()
   
   # The posterior over the differences in mu, and the probability that
   # the difference is below/above zero
   delta_mu = {}
   P_dle0 = {}
   P_dge0 = {}
   max_delta_mu = -np.inf
   for catapult_pair in catapult_pairs:
      unnormalised_delta_mu = np.convolve(p_mu[catapult_pair[0]], np.flip(p_mu[catapult_pair[1]]))
      delta_mu[catapult_pair] = unnormalised_delta_mu / np.sum(unnormalised_delta_mu * delta_step_width)
      
      max_delta_mu = max(max_delta_mu, np.max(delta_mu[catapult_pair]))
      P_dle0[catapult_pair] = np.sum(delta_mu[catapult_pair][:n_steps] * delta_step_width)
      P_dge0[catapult_pair] = np.sum(delta_mu[catapult_pair][n_steps-1:] * delta_step_width)

   if plotting:
      fig, axs = plt.subplots(len(catapult_pairs), 2)
      for i in range(len(catapult_pairs)):
         catapult_pair = catapult_pairs[i]
         true_delta = mu[catapult_pair[0]] - mu[catapult_pair[1]]
         index_true_delta = np.searchsorted(delta_vector, true_delta, side='left')
         zoom_width = 2 * max(sigma[catapult_pair[0]], sigma[catapult_pair[1]])
      
         axs.flat[2*i].plot(delta_vector, delta_mu[catapult_pair])
         axs.flat[2*i].fill_between(delta_vector[n_steps-1:], delta_mu[catapult_pair][n_steps-1:])
         if delta_vector[index_true_delta] > 0:
            axs.flat[2*i].vlines(true_delta, 0, delta_mu[catapult_pair][index_true_delta], linestyles = 'dashed', colors = 'white')
         else:
            axs.flat[2*i].vlines(true_delta, 0, delta_mu[catapult_pair][index_true_delta], linestyles = 'dashed')
         axs.flat[2*i].vlines(true_delta, delta_mu[catapult_pair][index_true_delta], max_delta_mu * 1.1, linestyles = 'dashed')
         axs.flat[2*i].set_xlim(left = true_delta - zoom_width, right = true_delta + zoom_width)
         axs.flat[2*i].set_ylim(bottom = 0, top = max_delta_mu * 1.1)
         axs.flat[2*i].set(xlabel=r'$D$', ylabel=r'$d \left( D \right)$', title = r'$P\left( D > 0 \right) = {:.2f}$'.format(P_dge0[catapult_pair]))

         axs.flat[2*i+1].plot(delta_vector, delta_mu[catapult_pair])
         axs.flat[2*i+1].fill_between(delta_vector[:n_steps], delta_mu[catapult_pair][:n_steps])
         if delta_vector[index_true_delta] < 0:
            axs.flat[2*i+1].vlines(true_delta, 0, delta_mu[catapult_pair][index_true_delta], linestyles = 'dashed', colors = 'white')
         else:
            axs.flat[2*i+1].vlines(true_delta, 0, delta_mu[catapult_pair][index_true_delta], linestyles = 'dashed')
         axs.flat[2*i+1].vlines(true_delta, delta_mu[catapult_pair][index_true_delta], max_delta_mu * 1.1, linestyles = 'dashed')
         axs.flat[2*i+1].set_xlim(left = true_delta - zoom_width, right = true_delta + zoom_width)
         axs.flat[2*i+1].set_ylim(bottom = 0, top = max_delta_mu * 1.1)
         axs.flat[2*i+1].set(xlabel=r'$D$', ylabel=r'$d \left( D \right)$', title = r'$P\left( D < 0 \right) = {:.2f}$'.format(P_dle0[catapult_pair]))
      fig.set_size_inches(12, 4)
      fig.tight_layout()
      plt.savefig('./{}/{}_delta_posteriors.png'.format(plot_folder, plot_main_name))
      plt.close()
   return P_dge0
   
def catapult_long_run(mu_A, mu_B, sigma_A, sigma_B, n_throws, n_trials, plotting = True, plot_folder = 'differences_plots', plot_main_name = 'Catapult_comparison'):
   """
   This will run the catapult_comparison function repeatedly, testing the
   long-run frequency properties.
   """
   n_bins = int(np.floor(np.sqrt(n_trials)))

   P_dge0 = []
   for i in range(n_trials):
      P_dge0.append(compare_catapults(mu_A, mu_B, sigma_A, sigma_B, n_throws, plotting = False)[('A', 'B')])
   P_dge0 = np.asarray(P_dge0)
   
   f_A_probably_better = np.sum(P_dge0 > 0.5) / n_trials
   
   if plotting:
      fig, axs = plt.subplots()

      axs.hist(P_dge0, bins = n_bins)
      axs.set(xlabel=r'$P \left( D > 0 \right)$', ylabel=r'Antal', title = r'$f\left( P \left( D > 0 \right) > 0.5 \right) = {:.2f}$'.format(f_A_probably_better))
      top = axs.get_ylim()[1]
      axs.vlines(0.5, 0, top, linestyles = 'dashed', color = 'black')
      axs.set_xlim(0, 1)
      axs.set_ylim(0, top)
      fig.set_size_inches(12, 4)
      fig.tight_layout()
      plt.savefig('./{}/{}_histogram.png'.format(plot_folder, plot_main_name))
      plt.close()
   return P_dge0
   
def compare_coins(P_A, P_B, n_tosses, plotting = True, plot_folder = 'differences_plots', plot_main_name = 'Coins'):
   """
   Say that we have two coins A and B, and we want to know which one is
   better. We have decided that for our purposes the 'better' coin
   is the one that has the highest chance of coming up heads. We also
   believe that the probability of getting a certain number of heads over
   a certain number of tosses follows a binomial distribution.
   
   To figure out which one is best, we flip each coin n times and put
   the results into our statistical model, which gives us a posterior
   probability over P for each coin. Using that we can calculate the
   probability distribution over the differences in P. This then gives us
   the probability of one coin being better than the other.
   """
   def logB(alpha, beta):
      """
      The logarithm of the normalisation factor to the binomial likelihood
      """
      return sp.loggamma(alpha) + sp.loggamma(beta) - sp.loggamma(alpha + beta)

   if P_A > 1 or P_B > 1:
      print('Probabilities cannot be larger than one!')
      print('Values input were {} and {}'.format(P_A, P_B))
      return
   if P_A < 0 or P_B < 0:
      print('Probabilities cannot be smaller than zero!')
      print('Values input were {} and {}'.format(P_A, P_B))
      return
   coins = ['A', 'B']
   P = {'A':abs(P_A), 'B':abs(P_B)}
   
   # Everything below here should be agnostic as to the number of coins
   
   coin_pairs = list(itertools.combinations(coins, 2))

   # Generate tosses for each coin
   heads = {}
   for coin in coins:
      heads[coin] = np.sum(rd.uniform(0., 1., size = n_tosses) < P[coin])
      
   # Make a vector of the possible values of P
   n_steps = 1000
   P_vector = np.linspace(0., 1., num = n_steps)
   delta_steps = 2 * n_steps - 1
   delta_vector = np.linspace(-1, 1, num=delta_steps)   
   
   # The log-prior P(P). To stay consistent with a frequentist analysis, we
   # use a flat prior.
   log_prior = {}
   for coin in coins:
      log_prior[coin] = np.zeros(n_steps)
      
   # The log-likelihood P(successes|P)
   log_L = {}
   for coin in coins:
      tails = n_tosses - heads[coin]
      with np.errstate(divide = 'ignore'):
         log_L[coin] = heads[coin] * np.log(P_vector) + tails * np.log(1 - P_vector) - logB(heads[coin] + 1, tails + 1)
         if heads[coin] > 0:
            log_L[coin][0] = - np.inf
         else:
            log_L[coin][0] = - logB(heads[coin] + 1, tails + 1)
         if tails > 0:
            log_L[coin][-1] = - np.inf
         else:
            log_L[coin][-1] = - logB(heads[coin] + 1, tails + 1)

   # The full posterior over P
   log_pP = {}
   pP = {}
   pP_max = -np.inf
   for coin in coins:
      log_pP[coin] = log_prior[coin] + log_L[coin]
      pP[coin] = np.exp(log_pP[coin])
      pP_max = max(pP_max, np.max(pP[coin]))

   if plotting:
      fig, axs = plt.subplots(1, len(coins))
      for i in range(len(coins)):
         coin = coins[i]
   
         axs.flat[i].plot(P_vector, pP[coin])
         for coin_2 in coins:
            true_P = P[coin_2]
            if coin_2 == coin:
               linestyles = 'solid'
            else:
               linestyles = 'dashed'
            axs.flat[i].vlines(true_P, 0, pP_max * 1.1, linestyles = linestyles)
         axs.flat[i].set_xlim(left = 0, right = 1)
         axs.flat[i].set_ylim(bottom = 0, top = pP_max * 1.1)
         axs.flat[i].set(xlabel=r'$P$', ylabel=r'$P\left( P \right)$', title = r'$p(P|kast)$ (Mynt {})'.format(coin))
      fig.set_size_inches(12, 4)
      fig.tight_layout()
      plt.savefig('./{}/{}_P_posteriors.png'.format(plot_folder, plot_main_name))
      plt.close()
   
   # The posterior over the differences in P, and the probability that
   # the difference is below/above zero
   delta_P = {}
   P_dle0 = {}
   P_dge0 = {}
   max_delta_P = -np.inf
   for coin_pair in coin_pairs:
      delta_P[coin_pair] = np.convolve(pP[coin_pair[0]], np.flip(pP[coin_pair[1]]))
      P_dle0[coin_pair] = np.sum(delta_P[coin_pair][:n_steps]) / np.sum(delta_P[coin_pair])
      P_dge0[coin_pair] = np.sum(delta_P[coin_pair][n_steps-1:]) / np.sum(delta_P[coin_pair])
      max_delta_P = max(max_delta_P, np.max(delta_P[coin_pair]))
   
   if plotting:
      fig, axs = plt.subplots(len(coin_pairs), 2)
      for i in range(len(coin_pairs)):
         coin_pair = coin_pairs[i]
         true_delta = P[coin_pair[0]] - P[coin_pair[1]]
         index_true_delta = np.searchsorted(delta_vector, true_delta, side='left')
      
         axs.flat[2*i].plot(delta_vector, delta_P[coin_pair])
         axs.flat[2*i].fill_between(delta_vector[n_steps-1:], delta_P[coin_pair][n_steps-1:])
         if delta_vector[index_true_delta] > 0:
            axs.flat[2*i].vlines(true_delta, 0, delta_P[coin_pair][index_true_delta], linestyles = 'dashed', colors = 'white')
         else:
            axs.flat[2*i].vlines(true_delta, 0, delta_P[coin_pair][index_true_delta], linestyles = 'dashed')
         axs.flat[2*i].vlines(true_delta, delta_P[coin_pair][index_true_delta], max_delta_P * 1.1, linestyles = 'dashed')
         axs.flat[2*i].set_xlim(left = -1, right = 1)
         axs.flat[2*i].set_ylim(bottom = 0, top = max_delta_P * 1.1)
         axs.flat[2*i].set(xlabel=r'$\Delta P$', ylabel=r'$P \left( \Delta P \right)$', title = r'$P\left( \Delta P > 0 \right) = {:.2f}$'.format(P_dge0[coin_pair]))

         axs.flat[2*i+1].plot(delta_vector, delta_P[coin_pair])
         axs.flat[2*i+1].fill_between(delta_vector[:n_steps], delta_P[coin_pair][:n_steps])
         if delta_vector[index_true_delta] > 0:
            axs.flat[2*i+1].vlines(true_delta, 0, delta_P[coin_pair][index_true_delta], linestyles = 'dashed')
         else:
            axs.flat[2*i+1].vlines(true_delta, 0, delta_P[coin_pair][index_true_delta], linestyles = 'dashed', colors = 'white')
         axs.flat[2*i+1].vlines(true_delta, delta_P[coin_pair][index_true_delta], max_delta_P * 1.1, linestyles = 'dashed')
         axs.flat[2*i+1].set_xlim(left = -1, right = 1)
         axs.flat[2*i+1].set_ylim(bottom = 0, top = max_delta_P * 1.1)
         axs.flat[2*i+1].set(xlabel=r'$\Delta P$', ylabel=r'$P \left( \Delta P \right)$', title = r'$P\left( \Delta P < 0 \right) = {:.2f}$'.format(P_dle0[coin_pair]))
      fig.set_size_inches(12, 4)
      fig.tight_layout()
      plt.savefig('./{}/{}_delta_posteriors.png'.format(plot_folder, plot_main_name))
      plt.close()
   return P_dge0
   
def coin_long_run(P_A, P_B, n_tosses, n_trials, plotting = True, plot_folder = 'differences_plots', plot_main_name = 'Coin_comparison'):
   """
   This will run the coin_comparison function repeatedly, testing the
   long-run frequency properties.
   """
   
   # Only n_tosses different trial outcomes are actually possible, so
   # having more bins than that creates an oddly spiked histogram.
   n_bins = min(int(np.floor(np.sqrt(n_trials))), n_tosses // 2)

   P_dge0 = []
   for i in range(n_trials):
      P_dge0.append(compare_coins(P_A, P_B, n_tosses, plotting = False)[('A', 'B')])
   P_dge0 = np.asarray(P_dge0)
   
   f_A_probably_better = np.sum(P_dge0 > 0.5) / n_trials
   
   if plotting:
      fig, axs = plt.subplots()

      axs.hist(P_dge0, bins = n_bins)
      axs.set(xlabel=r'$P \left( D > 0 \right)$', ylabel=r'Antal', title = r'$f\left( P \left( D > 0 \right) > 0.5 \right) = {:.2f}$'.format(f_A_probably_better))
      top = axs.get_ylim()[1]
      axs.vlines(0.5, 0, top, linestyles = 'dashed', color = 'black')
      axs.set_xlim(0, 1)
      axs.set_ylim(0, top)
      fig.set_size_inches(12, 4)
      fig.tight_layout()
      plt.savefig('./{}/{}_histogram.png'.format(plot_folder, plot_main_name))
      plt.close()
   return P_dge0
   
