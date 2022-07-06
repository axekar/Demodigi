"""
This script was written for the ESF-financed project Demokratisk
Digitalisering. The project is a collaboration between
Arbetsförmedlingen (AF) and Kungliga Tekniska Högskolan (KTH). The
purpose of the project is to increase the digital competence - as
defined at https://ec.europa.eu/jrc/en/digcomp - of people working at
Arbetsförmedlingen and by extension also job seekers. This will be
done by learning modules at KTH using OLI-Torus.

--- About this Python module ---

This Python module implements a toy model that demonstrates the results
of a couple of different fitting procedures.

Written by Alvin Gavel
https://github.com/Alvin-Gavel/Demodigi
"""

import numpy as np
import numpy.random as rd
import matplotlib.pyplot as plt



class experiment:
   """
   This represents the experiment and the following fitting of a model to
   the observed data.
   
   User-defined attributes
   --------------------------------------
   alpha : float
   \tThe angle of the line with respect to the x-axis.
   n : int
   \tThe number of measurements taken
   sigma : float
   \tThe standard deviation in the random scatter. Note that for
   \tsimplicity the analysis assumes that this is known.
   n_steps : int
   \tThe number of steps to use in numerical calculations
   plot_folder : str
   \tPath to the folder where all plots should be placed.
   
   Attributes defined automatically, which should not be changed
   -------------------------------------------------------------
   alpha_range : float ndarray
   \tRange of values of the parameter alpha used when fitting
   r_range : float ndarray
   \tRange of values of radial distance r used when estimating
   \talpha
   a_range : float ndarray
   \tRange of values of the parameter a used when fitting
   
   Attributes defined when experiment in run
   -----------------------------------------
   measurements : float ndarray
   \tSimulated measurements made in the experiment
   x_absmax : float
   \tLargest deviation from the origin along the x-axis
   y_absmax : float
   \tLargest deviation from the origin along the y-axis
   \tabsmax : float
   \tLargest deviation from the origin along either axis
   likelihood_alpha : float ndarray
   \tLikelihood of data as a function of the alphas stored in alpha_range
   alpha_frequentist_best_fit : float
   \tMaximum-likelihood best estimate of alpha
   posterior_alpha : float ndarray
   \tPosterior probability of the alphas stored in alpha_range
   likelihood_a : float ndarray
   \tLikelihood of data as a function of the as stored in alpha_range
   a_frequentist_best_fit : float
   \tMaximum-likelihood best estimate of a
   posterior_a : float ndarray
   \tPosterior probability of the as stored in a_range
   """
   def __init__(self, alpha, n, sigma, n_steps = 1000, plot_folder = 'parameter_fitting_plots'):
      self.alpha = alpha
      self.a = np.tan(alpha)
      self.n = n
      self.sigma = sigma
      self.n_steps = n_steps
      
      # These are used in the fit that describes the line in terms of the
      # angle alpha
      self.alpha_range = np.linspace(0., np.pi/2., num = self.n_steps)
      self.r_range = np.linspace(0., 1., num = self.n_steps)
      
      # These are used in the fit that describes the line in terms of the
      # slope a
      self.a_range = np.linspace(0., 10., num = self.n_steps)
      
      self.plot_folder = plot_folder
      self.run()
      return


   ### Statistics functions
   
   def run(self):
      """
      Run the simulated experiment and run the different fits to the
      simulated data
      """
      self._generate_measurements()
      self._calculate_likelihood_alpha()
      self._calculate_posterior_alpha()
      self._frequentist_fit_alpha()
      self._bayesian_fit_alpha()
      self._calculate_likelihood_a()
      self._calculate_posterior_a()
      self._frequentist_fit_a()
      self._bayesian_fit_a()
      return
   
   def _generate_measurements(self):
      r = rd.uniform(low = 0., high = 1., size = self.n)
      x = r * np.cos(self.alpha) + rd.normal(loc=0.0, scale=self.sigma, size=self.n)
      y = r * np.sin(self.alpha) + rd.normal(loc=0.0, scale=self.sigma, size=self.n)
      self.measurements = np.asarray(list(zip(x, y)))
      self.x_absmax = np.max(np.absolute(x))
      self.y_absmax = np.max(np.absolute(y))
      self.absmax = max(self.x_absmax, self.y_absmax)
      return 
   
   def distance_squared(self, x_true, y_true, x, y):
      return (x_true - x)**2 + (y_true - y)**2

   def P_scatter_given_true(self, x_true, y_true, x, y):
      d2 = self.distance_squared(x_true, y_true, x, y)
      return (1. / (self.sigma * np.sqrt(2 * np.pi))) * np.exp(- d2 / (2 * self.sigma**2))

   # Fitting procedure using the parametrisation with alpha
   
   def _calculate_likelihood_alpha(self):
      # Note to self: I may rewrite this as a n_steps x n matrix, so that
      # we can easily check the effect of analysing subsets of the data.
      self.likelihood_alpha = np.ones(self.n_steps)
      
      for i in range(self.n_steps):
         alpha = self.alpha_range[i]
         x_true_range = self.r_range * np.cos(alpha)
         y_true_range = self.r_range * np.sin(alpha)
         for j in range(self.n):
            x = self.measurements[j,0]
            y = self.measurements[j,1]
            integrand = self.P_scatter_given_true(x_true_range, y_true_range, x, y)
            P = np.trapz(integrand, x=self.r_range)
            self.likelihood_alpha[i] *= P
      return
      
   def _frequentist_fit_alpha(self):
      self.alpha_frequentist_best_fit = self.alpha_range[np.argmax(self.likelihood_alpha)]
      return
      
   def _calculate_posterior_alpha(self):
      self.posterior_alpha = self.likelihood_alpha * np.ones(self.n_steps) * np.trapz(self.likelihood_alpha, x=self.alpha_range)
      return
      
   def _bayesian_fit_alpha(self):
      self.alpha_bayesian_best_fit = self.alpha_range[np.argmax(self.posterior_alpha)]
      return
      
   # Fitting procedure using the parametrisation with a
   
   def _calculate_likelihood_a(self):
      self.likelihood_a = np.ones(self.n_steps)
      
      for i in range(self.n_steps):
         a = self.a_range[i]
         x_end = 1. / np.sqrt(1. + a**2)
         x_true_range = np.linspace(0., x_end)
         y_true_range = a * x_true_range
         for j in range(self.n):
            x = self.measurements[j,0]
            y = self.measurements[j,1]
            P_xy_a = self.P_scatter_given_true(x_true_range, y_true_range, x, y)
            P_x = np.sqrt(1. + a**2)
            P = np.trapz(P_xy_a * P_x, x=x_true_range)
            self.likelihood_a[i] *= P
      return
      
   def _frequentist_fit_a(self):
      self.a_frequentist_best_fit = self.a_range[np.argmax(self.likelihood_a)]
      return
      
   def _calculate_posterior_a(self):
      self.posterior_a = self.likelihood_a * np.ones(self.n_steps) * np.trapz(self.likelihood_a, x=self.a_range)
      return
      
   def _bayesian_fit_a(self):
      self.a_bayesian_best_fit = self.a_range[np.argmax(self.posterior_a)]
      return

      
   ### Plotting functions
      
   def plot(self):
      """
      Plot the simulated data, and the different fits to the data
      """
      self.plot_data()
      self.plot_likelihood_scatter()
      self.plot_likelihood_alpha()
      self.plot_posterior_alpha()
      self.plot_likelihood_a()
      self.plot_posterior_a()
      self.plot_fits()
      return
   
   def plot_data(self):
      plt.clf()
      plt.tight_layout()
      plt.scatter(self.measurements[:,0], self.measurements[:,1], s=1, marker = 's')
      plt.scatter([0, np.cos(self.alpha)], [0, np.sin(self.alpha)], c = 'k')
      plt.plot([0, np.cos(self.alpha)], [0, np.sin(self.alpha)], c = 'k', linestyle = '--')
      plt.xlim(-max(1, self.absmax), max(1, self.absmax))
      plt.ylim(-max(1, self.absmax), max(1, self.absmax))
      plt.xlabel(r'$x$')
      plt.ylabel(r'$y$') 
      plt.savefig('./{}/Measurements.png'.format(self.plot_folder))
      return
      
   def plot_fits(self):
      plt.clf()
      plt.tight_layout()
      plt.plot([0, np.cos(self.alpha)], [0, np.sin(self.alpha)], c = 'k', linestyle = '--', label = 'Sann')
      plt.scatter(self.measurements[:,0], self.measurements[:,1], s=1, marker = 's')
      plt.scatter([0, np.cos(self.alpha)], [0, np.sin(self.alpha)], c = 'k')
      plt.plot([0, np.cos(self.alpha_bayesian_best_fit)], [0, np.sin(self.alpha_bayesian_best_fit)], c = 'b', linestyle = '-', label = r'Bayesiansk, $\alpha$')
      plt.plot([0, np.cos(self.alpha_frequentist_best_fit)], [0, np.sin(self.alpha_frequentist_best_fit)], c = 'b', linestyle = '--', label = r'Frekventistisk, $\alpha$')
      plt.plot([0, 1. / np.sqrt(1. + self.a_bayesian_best_fit**2)], [0, self.a_bayesian_best_fit / np.sqrt(1. + self.a_bayesian_best_fit**2)], c = 'r', linestyle = '-', label = r'Bayesiansk, $a$')
      plt.plot([0, 1. / np.sqrt(1. + self.a_frequentist_best_fit**2)], [0, self.a_frequentist_best_fit / np.sqrt(1. + self.a_frequentist_best_fit**2)], c = 'r', linestyle = '--', label = r'Frekventistisk, $a$')
      plt.xlim(-max(1, self.absmax), max(1, self.absmax))
      plt.ylim(-max(1, self.absmax), max(1, self.absmax))
      plt.xlabel(r'$x$')
      plt.ylabel(r'$y$') 
      plt.legend()
      plt.savefig('./{}/Best_fits.png'.format(self.plot_folder))
      return
   
   def plot_likelihood_scatter(self):
      x_true_grid, y_true_grid = np.meshgrid(np.linspace(0, 1, self.n_steps), np.linspace(0, 1, self.n_steps))
      
      for i in range(self.n):
         x = self.measurements[i,0]
         y = self.measurements[i,1]
         P_scatter = self.P_scatter_given_true(x_true_grid, y_true_grid, x, y)
         plt.clf()
         plt.tight_layout()
         plt.pcolormesh(x_true_grid, y_true_grid, P_scatter, shading = 'nearest')
         plt.scatter(self.measurements[:,0], self.measurements[:,1], c = 'w', edgecolors = 'k')
         plt.xlim(0, 1)
         plt.ylim(0, 1)
         plt.xlabel(r'$x$')
         plt.ylabel(r'$y$')         
         plt.savefig('./{}/Likelihood_scatter_{}.png'.format(self.plot_folder, i))
      return
      
   def plot_likelihood_alpha(self):
      plt.clf()
      plt.tight_layout()
      plt.plot(self.alpha_range, self.likelihood_alpha, c = 'b', linestyle = '--')
      plt.vlines(self.alpha, 0, np.max(self.likelihood_alpha), colors='k', linestyles='--')
      plt.xlim(0, np.pi/2)
      plt.xlabel(r'$\alpha$')
      plt.ylabel(r'$P \left( x, y | \alpha \right)$')
      plt.savefig('./{}/Likelihood_alpha.png'.format(self.plot_folder))
      return
      
   def plot_posterior_alpha(self):
      plt.clf()
      plt.tight_layout()
      plt.plot(self.alpha_range, self.posterior_alpha, c = 'b', linestyle = '-')
      plt.vlines(self.alpha, 0, np.max(self.posterior_alpha), colors='k', linestyles='--')
      plt.xlim(0, np.pi/2)
      plt.xlabel(r'$\alpha$')
      plt.ylabel(r'$P \left( \alpha | x, y \right)$')
      plt.savefig('./{}/Posterior_alpha.png'.format(self.plot_folder))
      return
      
   def plot_likelihood_a(self):
      plt.clf()
      plt.tight_layout()
      plt.plot(self.a_range, self.likelihood_a, c = 'r', linestyle = '--')
      plt.vlines(self.a, 0, np.max(self.likelihood_a), colors='k', linestyles='--')
      index_max = np.argmax(self.likelihood_a)
      plt.xlim(0, self.a_range[min(index_max * 2, self.n_steps - 1)])
      plt.xlabel(r'$a$')
      plt.ylabel(r'$P \left( x, y | a \right)$')
      plt.savefig('./{}/Likelihood_a.png'.format(self.plot_folder))
      return
      
   def plot_posterior_a(self):
      plt.clf()
      plt.tight_layout()
      plt.plot(self.a_range, self.posterior_a, c = 'r', linestyle = '-')
      plt.vlines(self.a, 0, np.max(self.posterior_a), colors='k', linestyles='--')
      index_max = np.argmax(self.posterior_a)
      plt.xlim(0, self.a_range[min(index_max * 2, self.n_steps - 1)])
      plt.xlabel(r'$a$')
      plt.ylabel(r'$P \left( a | x, y \right)$')
      plt.savefig('./{}/Posterior_a.png'.format(self.plot_folder))
      return
