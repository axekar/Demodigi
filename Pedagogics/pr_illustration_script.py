"""
This is a script that uses the module priors to generate the plots
in the internal Demokratisk Digitalisering document "Ojämna priors,
platta priors eller inga priors".
"""

import numpy as np
import priors as pr

toy_model = pr.experiment(np.pi / 4., 4, 0.1)
toy_model.plot()
