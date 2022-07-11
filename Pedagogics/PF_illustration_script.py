"""
This is a script that uses the module parameter_fitting to investigate
the results of a number of different methods of parameter fitting.
"""

import numpy as np
import parameter_fitting as pf

toy_model = pf.experiment(np.pi / 4., 4, 0.1)
toy_model.plot()
