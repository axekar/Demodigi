"""
This module was written for the ESF-financed project Demokratisk
Digitalisering. The project is a collaboration between
Arbetsförmedlingen (AF) and Kungliga Tekniska Högskolan (KTH). The
purpose of the project is to increase the digital competence - as
defined at https://ec.europa.eu/jrc/en/digcomp - of people working at
Arbetsförmedlingen, and by extension also job seekers. This will be
done by learning modules at KTH using OLI-Torus.

--- About this Python module ---

This module is intended to do preprocessing of data our data - for
example that coming out of OLI-Torus - so that it can be used by the
factorial_experiment module. While doing so it should also output a
directory tree with plots of data that we believe is of interest.

Written by Alvin Gavel,

https://github.com/Alvin-Gavel/Demodigi
"""

import numpy as np
import pandas as pd
   
class participant:
   """
   This represents a single person taking a learning module.
   
   Attributes
   ----------
   ID : string
   \tSome unique identifier of the participant. For privacy reasons, this
   \tis unlikely to be their actual name.
   """
   def __init__(self, ID):
      self.ID = ID
      self.correct_first_try = {}
      return
   
class skill:
   """
   This represents a specific skill that the learning module is intended
   to teach. The skill is assumed to be tested once per session of the
   module.
   
   Attributes
   ----------
   name : string
   \tSome name of the skill, which is used to identify questions testing
   \tthat skill in the data output by OLI-Torus
   """
   def __init__(self, name):
      self.name = name
      return
   

class learning_module:
   """
   This represents one learning module in the project.
  
   Attributes
   ----------
   questions : list of string
   \tA list of the questions given in the learning module, as identified
   \tin the "Activity Title" column in the output from OLI-Torus
   participants : list of participant
   \tA list of the people taking the learning module, as identified in the
   \t"Student ID" column in the output from OLI-Torus
   """
   def __init__(self, questions, participants):
      self.questions = questions
      self.participants = participants
      self.full_results = None
      self.results_read = False
      return
      
   def import_oli_results(self, filepath):
      """
      Import a file with the raw statistics directly out of OLI-Torus, in the
      tab-separated values format.
      """
      self.full_results = pd.read_csv(filepath, sep='\t')
      self.results_read = True
      return
   
   def _read_participant_results(self, participant):
      """
      Find out, for each question, whether a specific participant got it
      right on the first try.
      """
      participant.correct_first_try = {}
      correct_participant = self.full_results[self.full_results['Student ID'] == participant.ID]
      for question in self.questions:
         try:
            correct_question = correct_participant[correct_participant['Activity Title'] == question]
            got_it = correct_question["Correct?"][correct_question["Attempt Number"] == 1].to_numpy()[0]
         except IndexError:
            got_it = False
         participant.correct_first_try[question] = got_it
      return
      
   def read_participants_results(self):
      """
      Find out, for each question, whether the participants got it right on
      the first try.
      """
      if not self.results_read:
         print('No results to read!')
         return

      for participant in self.participants:
         self._read_participant_results(participant)
      return
