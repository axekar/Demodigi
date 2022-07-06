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
import imageio


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
   likelihood : dict of float ndarray
   \tLikelihood of data as a function of the parameter values
   posterior : dict of float ndarray
   \tPosterior of parameter values
   posterior_CDF : dict of float ndarray
   \tCumulative distribution function of the posterior probability
   best_fits : dict of dicts of floats
   \tDictionaries containing the best fits of alpha and a using different
   \tmethods
   """
   def __init__(self, alpha, n, sigma, n_steps = 10000, plot_folder = 'parameter_fitting_plots'):
      self.true_values = {'alpha': alpha, 'a':np.tan(alpha)}
      self.n = n
      self.sigma = sigma
      self.n_steps = n_steps
      
      self.parameter_range = {'alpha':np.linspace(0., np.pi/2., num = self.n_steps),
      				'a':np.linspace(0., self.true_values['a'] * 10, num = self.n_steps)}
      self.r_range = np.linspace(0., 1., num = self.n_steps)

      self.likelihood = {}
      self.prior = {'alpha':{'flat':np.ones(self.n_steps)},
      		     'a':{'flat':np.ones(self.n_steps), 'non-informative': (1./np.pi) * (1. / (1 + self.parameter_range['a']))}}
      self.posterior = {}
      self.posterior_CDF = {}
      self.best_fits = {'alpha':{}, 'a':{}}
      
      self.plot_folder = plot_folder
      self.run()

      self._parameter_to_latex = {'a':r'a', 'alpha':r'\alpha'}

      return


   ### Convenience functions
 
   def a_to_alpha(self, a):
      return np.arctan(a)
      
   def alpha_to_a(self, alpha):
      return np.tan(alpha)

   

   def _calculate_CDF(self, parameter_range, PDF):
      """
      This is *not* computationally efficient
      """
      n_points = len(parameter_range)
      CDF = np.zeros(n_points)
      for i in range(n_points-1):
         CDF[i+1] = np.trapz(PDF[0:i], x=parameter_range[0:i])
      return CDF
      

   ### Statistics functions
   
   def run(self):
      """
      Run the simulated experiment and run the different fits to the
      simulated data
      """
      self._generate_measurements()
      self._calculate_likelihood_alpha()
      self._calculate_likelihood_a()
      self._calculate_posteriors()
      self._maximum_likelihood_fit()
      self._maximum_posterior_fit()
      self._median_posterior_fit()
      return
   
   def _generate_measurements(self):
      r = rd.uniform(low = 0., high = 1., size = self.n)
      x = r * np.cos(self.true_values['alpha']) + rd.normal(loc=0.0, scale=self.sigma, size=self.n)
      y = r * np.sin(self.true_values['alpha']) + rd.normal(loc=0.0, scale=self.sigma, size=self.n)
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


   ### Calculations of likelihoods and posteriors
   
   def _calculate_likelihood_alpha(self):
      self.likelihood['alpha'] = np.ones(self.n_steps)
      
      for i in range(self.n_steps):
         alpha = self.parameter_range['alpha'][i]
         x_true_range = self.r_range * np.cos(alpha)
         y_true_range = self.r_range * np.sin(alpha)
         for j in range(self.n):
            x = self.measurements[j,0]
            y = self.measurements[j,1]
            integrand = self.P_scatter_given_true(x_true_range, y_true_range, x, y)
            P = np.trapz(integrand, x=self.r_range)
            self.likelihood['alpha'][i] *= P
      return
      
   def _calculate_likelihood_a(self):
      self.likelihood['a'] = np.ones(self.n_steps)
      
      for i in range(self.n_steps):
         a = self.parameter_range['a'][i]
         x_end = 1. / np.sqrt(1. + a**2)
         x_true_range = np.linspace(0., x_end)
         y_true_range = a * x_true_range
         for j in range(self.n):
            x = self.measurements[j,0]
            y = self.measurements[j,1]
            P_xy_a = self.P_scatter_given_true(x_true_range, y_true_range, x, y)
            P_x = np.sqrt(1. + a**2)
            P = np.trapz(P_xy_a * P_x, x=x_true_range)
            self.likelihood['a'][i] *= P
      return

   def _calculate_posteriors(self):
      for parameter in ['alpha', 'a']:
         self.posterior[parameter] = {}
         self.posterior_CDF[parameter] = {}
         for prior_name, prior_vector in self.prior[parameter].items():
            unnormalised_posterior = self.likelihood[parameter] * prior_vector
            self.posterior[parameter]['{} prior'.format(prior_name)] = unnormalised_posterior / np.trapz(unnormalised_posterior, x=self.parameter_range[parameter])
            self.posterior_CDF[parameter]['{} prior'.format(prior_name)] = self._calculate_CDF(self.parameter_range[parameter], self.posterior[parameter]['{} prior'.format(prior_name)])
      return


   ### Fitting procedures
      
   def _maximum_likelihood_fit(self):
      for parameter in ['alpha', 'a']:
         self.best_fits[parameter]['Maximum likelihood'] = self.parameter_range[parameter][np.argmax(self.likelihood[parameter])]
      return
      

   def _maximum_posterior_fit(self):
      for parameter in ['alpha', 'a']:
         for prior_name in self.prior[parameter].keys():
            self.best_fits[parameter]['Maximum posterior, {} prior'.format(prior_name)] = self.parameter_range[parameter][np.argmax(self.posterior[parameter]['{} prior'.format(prior_name)])]
      return
      
   def _median_posterior_fit(self):
      for parameter in ['alpha', 'a']:
         for prior_name in self.prior[parameter].keys():
            where_above = np.where(self.posterior_CDF[parameter]['{} prior'.format(prior_name)] > 0.5)
            first_above_index = where_above[0][0]
            self.best_fits[parameter]['Median posterior, {} prior'.format(prior_name)] = self.parameter_range[parameter][first_above_index]
      return
      

   ### Plotting functions
      
   def plot(self):
      """
      Plot the simulated data, and the different fits to the data
      """
      self.plot_data()
      self.plot_likelihood_scatter()
      self.makegif_likelihood_scatter()
      self.plot_likelihood()
      self.plot_posterior()
      self.plot_all_fits()
      self.plot_fits_with_highlight()
      self.makegif_fits()
      return
   
   def plot_data(self):
      plt.clf()
      plt.scatter(self.measurements[:,0], self.measurements[:,1], s=1, marker = 's')
      plt.scatter([0, np.cos(self.true_values['alpha'])], [0, np.sin(self.true_values['alpha'])], c = 'k')
      plt.plot([0, np.cos(self.true_values['alpha'])], [0, np.sin(self.true_values['alpha'])], c = 'k', linestyle = '--')
      plt.xlim(-max(1, self.absmax), max(1, self.absmax))
      plt.ylim(-max(1, self.absmax), max(1, self.absmax))
      plt.xlabel(r'$x$')
      plt.ylabel(r'$y$') 
      plt.gca().set_aspect('equal', adjustable='box')
      plt.tight_layout()
      plt.savefig('./{}/Measurements.png'.format(self.plot_folder))
      return
   
   def likelihood_scatter_plotpath(self, i):
      return './{}/Likelihood_scatter_{}.png'.format(self.plot_folder, i)
   
   def plot_likelihood_scatter(self):
      x_true_grid, y_true_grid = np.meshgrid(np.linspace(0, 1, int(np.sqrt(self.n_steps))), np.linspace(0, 1, int(np.sqrt(self.n_steps))))
      
      for i in range(self.n):
         x = self.measurements[i,0]
         y = self.measurements[i,1]
         P_scatter = self.P_scatter_given_true(x_true_grid, y_true_grid, x, y)
         plt.clf()
         plt.pcolormesh(x_true_grid, y_true_grid, P_scatter, shading = 'nearest')
         plt.scatter(self.measurements[:,0], self.measurements[:,1], c = 'w', edgecolors = 'k')
         plt.xlim(0, 1)
         plt.ylim(0, 1)
         plt.xlabel(r'$x$')
         plt.ylabel(r'$y$')         
         plt.gca().set_aspect('equal', adjustable='box')
         plt.tight_layout()
         plt.savefig(self.likelihood_scatter_plotpath(i))
      return
      
   def makegif_likelihood_scatter(self):
      plots = []
      for i in range(self.n):
         plots.append(imageio.imread(self.likelihood_scatter_plotpath(i)))
      imageio.mimsave('./{}/Likelihood_scatter.gif'.format(self.plot_folder), plots, duration=2)
      return
   
   def plot_likelihood(self):
      for parameter in ['alpha', 'a']:
         plt.clf()
         ymax = np.max(self.likelihood[parameter]) * 1.1
         plt.vlines(self.true_values[parameter], 0, ymax, colors='k', linestyles='--', label = 'True value')
         plt.plot(self.parameter_range[parameter], self.likelihood[parameter], c = 'b', linestyle = '-', label = 'Likelihood')
         plt.vlines(self.best_fits[parameter]['Maximum likelihood'], 0, ymax, colors='b', linestyles='--', label = 'Max. likelihood')
         plt.xlim(self.parameter_range[parameter][0], 2 * self.true_values[parameter])
         plt.ylim(0, ymax)
         plt.xlabel(r'${}$'.format(self._parameter_to_latex[parameter]))
         plt.ylabel(r'$P \left( x, y | {} \right)$'.format(self._parameter_to_latex[parameter]))
         plt.legend()
         plt.tight_layout()
         plt.savefig('./{}/Likelihood_{}.png'.format(self.plot_folder, parameter))
      return
      
   def plot_posterior(self):
      for parameter in ['alpha', 'a']:
         for prior_name in self.prior[parameter].keys():
            plt.clf()
            ymax = max(np.max(self.posterior[parameter]['{} prior'.format(prior_name)]), 1.0)
            plt.vlines(self.true_values[parameter], 0, np.max(self.posterior[parameter]['{} prior'.format(prior_name)]), colors='k', linestyles='--', label = 'True value')
            plt.plot(self.parameter_range[parameter], self.posterior[parameter]['{} prior'.format(prior_name)], c = 'b', linestyle = '-', label = 'Posterior PDF')
            plt.plot(self.parameter_range[parameter], self.posterior_CDF[parameter]['{} prior'.format(prior_name)], c = 'r', linestyle = '-', label = 'Posterior CDF')
            plt.vlines(self.best_fits[parameter]['Maximum posterior, {} prior'.format(prior_name)], 0, ymax, colors='b', linestyles='--', label = 'Max. posterior')
            plt.vlines(self.best_fits[parameter]['Median posterior, {} prior'.format(prior_name)], 0, ymax, colors='r', linestyles='--', label = 'Med. posterior')
            plt.xlim(0, np.pi/2)
            plt.ylim(0, ymax)
            plt.xlabel(r'${}$'.format(self._parameter_to_latex[parameter]))
            plt.ylabel(r'$P \left( {} | x, y \right)$'.format(self._parameter_to_latex[parameter]))
            plt.legend()
            plt.tight_layout()
            plt.savefig('./{}/Posterior_{}_{}_prior.png'.format(self.plot_folder, parameter, prior_name))
      return
   
   def _get_fit_lines(self):
      fit_lines = {'a':{}, 'alpha':{}}
      for fit_method, alpha in self.best_fits['alpha'].items():
         fit_lines['alpha'][fit_method] = {}
         fit_lines['alpha'][fit_method]['x'] = [0, np.cos(alpha)]
         fit_lines['alpha'][fit_method]['y'] = [0, np.sin(alpha)]
         fit_lines['alpha'][fit_method]['label'] = r'{}, $\alpha$'.format(fit_method)
      for fit_method, a in self.best_fits['a'].items():
         x_end = 1. / np.sqrt(1 + a**2)
         y_end = a * x_end
         fit_lines['a'][fit_method] = {}
         fit_lines['a'][fit_method]['x'] = [0, x_end]
         fit_lines['a'][fit_method]['y'] = [0, y_end]
         fit_lines['a'][fit_method]['label'] =  r'{}, $a$'.format(fit_method)
      return fit_lines
   
   def plot_all_fits(self):
      fit_lines = self._get_fit_lines()
         
      plt.clf()
      plt.scatter(self.measurements[:,0], self.measurements[:,1], s=1, marker = 's')
      plt.scatter([0, np.cos(self.true_values['alpha'])], [0, np.sin(self.true_values['alpha'])], c = 'k')
      for parameter in ['a', 'alpha']:
         for fit_method in fit_lines[parameter].keys():
             dictionary = fit_lines[parameter][fit_method]
             plt.plot(dictionary['x'], dictionary['y'], linestyle = '-', label = dictionary['label'])
      plt.plot([0, np.cos(self.true_values['alpha'])], [0, np.sin(self.true_values['alpha'])], c = 'k', linestyle = '--', label = 'True line')
      plt.xlim(-max(1, self.absmax), max(1, self.absmax))
      plt.ylim(-max(1, self.absmax), max(1, self.absmax))
      plt.xlabel(r'$x$')
      plt.ylabel(r'$y$') 
      plt.legend(loc = 'lower left', prop={'size': 6})
      plt.gca().set_aspect('equal', adjustable='box')
      plt.tight_layout()
      plt.savefig('./{}/Best_fits.png'.format(self.plot_folder))
      return
      
   def fit_plotpath(self, parameter, fit_method):
      return './{}/Best_fit_{}_{}.png'.format(self.plot_folder, parameter, fit_method)
      
   def plot_fits_with_highlight(self):
      fit_lines = self._get_fit_lines()
         
      for parameter_1 in ['a', 'alpha']:
         for fit_method_1 in fit_lines[parameter_1].keys():
            plt.clf()
            plt.scatter(self.measurements[:,0], self.measurements[:,1], s=1, marker = 's')
            plt.scatter([0, np.cos(self.true_values['alpha'])], [0, np.sin(self.true_values['alpha'])], c = 'k')
            for parameter_2 in ['a', 'alpha']:
               for fit_method_2 in fit_lines[parameter_2].keys():
                  dictionary = fit_lines[parameter_2][fit_method_2]
                  if parameter_1 == parameter_2 and fit_method_1 == fit_method_2:
                     plt.plot(dictionary['x'], dictionary['y'], linestyle = '-', c = 'red', label = dictionary['label'], zorder=10)
                  else:
                     plt.plot(dictionary['x'], dictionary['y'], linestyle = '--', c = 'gray', label = dictionary['label'])

            plt.plot([0, np.cos(self.true_values['alpha'])], [0, np.sin(self.true_values['alpha'])], c = 'k', linestyle = '--', label = 'True line')
            plt.xlim(-max(1, self.absmax), max(1, self.absmax))
            plt.ylim(-max(1, self.absmax), max(1, self.absmax))
            plt.xlabel(r'$x$')
            plt.ylabel(r'$y$') 
            plt.legend(loc = 'lower left', prop={'size': 6})
            plt.gca().set_aspect('equal', adjustable='box')
            plt.tight_layout()
            plt.savefig(self.fit_plotpath(parameter_1, fit_method_1))
      return

   def makegif_fits(self):
      plots = []
      for parameter in ['a', 'alpha']:
         for fit_method in self.best_fits[parameter].keys():
            plots.append(imageio.imread(self.fit_plotpath(parameter, fit_method)))
      imageio.mimsave('./{}/Best_fits.gif'.format(self.plot_folder), plots, duration=2)
      return
