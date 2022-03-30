This repository contains code written for the ESF-financed project _Demokratisk Digitalisering_. The project is a collaboration between Arbetsförmedlingen (AF) and Kungliga Tekniska Högskolan (KTH). The purpose of the project is to increase the digital competence - as defined at https://ec.europa.eu/jrc/en/digcomp - of people working at AF, and by extension also job seekers. This will be done by learning modules at KTH using OLI-Torus.

The current contents of the repository are:

`README.md`: This text

`factorial_experiment.py`: Python module for analysing the results of a factorial experiment that we plan to do as part of the study. It can also be used for simulating similar studies, to test that the analysis at least makes sense on paper.

`FE_test_script.py`: Script intended as a test of the module `factorial_experiment`, by implementing a simple simulated study. It can also be seen as a demo of how to use the module. To make that easier, it has verbose comments explaining what happens at every step along the way.

`FE_simulation_script.py`: Script using the module `factorial_experiment` to simulate an experiment that we actually intend to do.

`behavioural_experiment.py`: Python module for simulating a behavioural experiment that we plan to do as part of the study. With time, I will also add code for analysis the results of the actual experiment.

`BE_test_script.py`: Script intended as a test of the module `behavioural_experiment`, by running some functions and plotting the results.
