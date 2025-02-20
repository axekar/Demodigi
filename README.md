This repository contains code written for the ESF-financed project _Demokratisk Digitalisering_. The project is a collaboration between Arbetsförmedlingen (AF) and Kungliga Tekniska Högskolan (KTH). The purpose of the project is to increase the digital competence - as defined at https://ec.europa.eu/jrc/en/digcomp - of people working at AF, and by extension also job seekers. This will be done by learning modules at KTH using OLI-Torus.

The current contents of the repository are:

`README.md`: This text

`factorial_experiment.py`: Python module for analysing the results of a factorial experiment that we plan to do as part of the study. It can also be used for simulating similar studies, to test that the analysis at least makes sense on paper.

`FE_demonstration_script.py`: Script that demonstrates the use of the module `factorial_experiment` by implementing a simple simulated study. To make that easier, it has verbose comments explaining what happens at every step along the way.

`FE_test_script.py`: Script for testing that the module `factorial_experiment` actually works as intended.

`FE_minimal_size_script.py`: Script using the module `factorial_experiment` to try to find the minimal number of participants that we need in order to measure the effects that we are interested in.

`KL_analysis_script.py`: Script for analysing data from the course module `Kartläggning`, which have already been rewritten into a format readable by the `Factorial_experiment` module by the module `preprocessing`, which is found in the directory `Utilities`

`IS_analysis__script.py`: Script for analysing data from the course module `IT-säkerhet`, which have already been rewritten into a format readable by the `Factorial_experiment` module by the module `preprocessing`, which is found in the directory `Utilities`

`behavioural_experiment.py`: Python module for simulating a behavioural experiment that we plan to do as part of the study. With time, I will also add code for analysing the results of the actual experiment.

`BE_test_script.py`: Script intended as a test of the module `behavioural_experiment`, by running some functions and plotting the results.

`Pedagogics`: Directory containing code written to demonstrate the underlying ideas behind our analysis.

`Utilities`: Directory containing code written to solve specific technical problems of no scientific interest.
