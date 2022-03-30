import behavioural_experiment as be

# Makes plots describing the simulated study
plot_results = True

single_try = be.experiment_run(100, 100, 0.5, 0.6)
if plot_results:
   single_try.plot_folder = 'DD_plots'
   single_try.plot_p()
   single_try.plot_d()

n_optimisation = be.varying_n(100, 1000, [0.5, 0.8, 0.85, 0.88], [0.6, 0.9, 0.9, 0.9], n_steps = 100, iterations = 10000)
if plot_results:
   n_optimisation.plot_folder = 'DD_plots'
   n_optimisation.run()
   n_optimisation.plot_pDpos()
