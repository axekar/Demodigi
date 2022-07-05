This directory contains code written to demonstrate some of the underlying ideas behind our statistical analysis.

The current contents of this directory are:

`README.md`: This text

`differences.py`: A module demonstrating the idea behind looking at the difference between two distributions that describe the effectiveness of two interventions

`df_illustration_script.py`: A script that uses the `differences` module to generate the plots used in the internal _Demokratisk Digitalisering_ document `Statistisk analys
av kvalitetsskillnader`.

`priors.py`: A module implementing a toy model that demonstrates a common misconception in statistical analysis: Bayesians often believe that they can avoid making assumptions by choosing a flat prior, and frequentists often believe that since they do not have a prior they automatically avoid making assumptions. The model shows that this is false, through an analysis where a number of statisticians fit the same model to the same data and end up with different results, irrespective of whether they are working in a frequentist framework or in Bayesian framework with a flat prior.
