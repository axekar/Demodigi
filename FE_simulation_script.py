"""
This script is intended to help identify the minimum number of
participants necessary to tell the effects of two manipulations that we
actually intend to do
"""

import factorial_experiment as fe


age = fe.simulated_background("old enough to have grown up without PC", fe.standard_transformations["slight deterioration"], fe.standard_transformations["no effect"], 0.25)
gender = fe.simulated_background("Is a guy", fe.standard_transformations["no effect"], fe.standard_transformations["no effect"], 0.5)
motivated = fe.simulated_background("low motivation", fe.standard_transformations["slight deterioration"], fe.standard_transformations["slight deterioration"], 0.20)

bounds = fe.boundaries(0.25, 0.5, minimum_quality_difference = 0.1)

AF = fe.simulated_participants(8000, 0.3, known_backgrounds = [age, gender, motivated], unknown_backgrounds = [], boundaries = bounds)

QBL_PQBL = fe.simulated_manipulation("Pure Question-based Learning", fe.standard_transformations["slight improvement"])
goals = fe.simulated_manipulation("Goal setting", fe.standard_transformations["slight improvement"])

simulated_study = fe.study('Simulation', AF, 40)
simulated_study.set_manipulations([QBL_PQBL, goals])
   
simulated_study.simulate_study(fe.standard_transformations["moderate improvement"])
simulated_study.do_tests()
simulated_study.summarise_results()
