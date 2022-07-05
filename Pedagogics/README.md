This directory contains code written to demonstrate some of the underlying ideas behind our statistical analysis.

The current contents of this directory are:

`README.md`: This text

`differences.py`: A module demonstrating the idea behind looking at the difference between two distributions that describe the effectiveness of two interventions

`df_illustration_script.py`: A script that uses the `differences` module to generate the plots used in the internal _Demokratisk Digitalisering_ document `Statistisk analys
av kvalitetsskillnader`.

`priors.py`: A module implementing a toy model that demonstrates a common misconception in Bayesian analysis: That it is possible to avoid making assumptions by choosing a flat prior. In reality, what is a flat prior depends on the choice of parametrisation of the underlying problem.
