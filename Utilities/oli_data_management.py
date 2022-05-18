"""
This module was written for the ESF-financed project Demokratisk
Digitalisering. The project is a collaboration between
Arbetsförmedlingen (AF) and Kungliga Tekniska Högskolan (KTH). The
purpose of the project is to increase the digital competence - as
defined at https://ec.europa.eu/jrc/en/digcomp - of people working at
Arbetsförmedlingen, and by extension also job seekers. This will be
done by learning modules at KTH using OLI-Torus.

--- About this Python module ---

This module is intended to read the tsv-files that come out of OLI-
TORUS, and transform them into json files that contain only the
information used by the factorial_experiment module.

Written by Alvin Gavel,

https://github.com/Alvin-Gavel/Demodigi
"""

import pandas as pd
   
class learning_module:
   """
   This represents one learning module in the project.
  
   Attributes
   ----------
   questions : list of string
   \tA list of the questions given in the learning module, as identified
   \tin the "Activity Title" column in the output from OLI-Torus
   questions : list of string
   \tA list of the people taking the learning module, as identified in the
   \t"Student ID" column in the output from OLI-Torus
   """
   def __init__(self, questions, participants):
      self.questions = questions
      self.participants = participants
      self.full_results = None
      return
      
   def import_oli_results(self, filepath):
      self.full_results = pd.read_csv(filepath, sep='\t')
      return
