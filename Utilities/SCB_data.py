"""
This module was written for the ESF-financed project Demokratisk
Digitalisering. The project is a collaboration between
Arbetsförmedlingen (AF) and Kungliga Tekniska Högskolan (KTH). The
purpose of the project is to increase the digital competence - as
defined at https://ec.europa.eu/jrc/en/digcomp - of people working at
Arbetsförmedlingen, and by extension also job seekers. This will be
done by learning modules at KTH using OLI-Torus.

--- About this Python module ---

We will need to report the progress to Statistiska Centralbyrån (SCB).
This will involve sending them a csv file with four columns stating for
each participant:

 1. The five-character code used to identify people at AF
 2. Starting date for the first module
 3. Estimated time spent on the first module (assumed to be 30min)
 4. Whether the participant has finished the first module

Written by Alvin Gavel,
https://github.com/Alvin-Gavel/Demodigi
"""

import pandas as pd

class SCB_data:
   """
   This represents the data that is of interest to SCB
   """
   def __init__(self):
      self.account_data = pd.DataFrame(columns = ['Femställig kod', 'Startdatum', 'Uppskattad tid', 'Avslutat läromodulen?'])
      self.full_results = pd.DataFrame([])
      self.results_read = False
      return
   
   def import_oli_results(self, filepath):
      """
      Import a file with the raw statistics directly out of OLI-Torus, in the
      tab-separated values format.
      """
      raw = pd.read_csv(filepath, sep='\t')
      self.full_results = raw.astype({"Student ID": str}) # This sometimes gets interpreted as int
      self.results_read = True
      return
