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

# Not used yet, but will become necessary later
import json
import matplotlib.pyplot as plt
   
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
   
class participant:
   """
   This represents a single person taking a learning module.
   
   Attributes
   ----------
   ID : string
   \tSome unique identifier of the participant. For privacy reasons, this
   \tis unlikely to be their actual name.
   correct_first_try : dict
   \tInitially empty dictionary stating for each question in a learning
   \tmodule whether the participant answered correctly on the first try.
   """
   def __init__(self, ID):
      self.ID = ID
      self.correct_first_try = pd.DataFrame()
      return

class learning_module:
   """
   This represents one learning module in the project.
  
   Attributes
   ----------
   skills : list of skill
   \tA list of the skills that the learning module aims to teach
   n_sessions : int
   \tThe number of sessions in the learning module. The assumption is that
   \tin each session each skill will be tested once
   participants : list of participant
   \tA list of the people taking the learning module, as identified in the
   \t"Student ID" column in the output from OLI-Torus
   full_results : pandas DataFrame
   \tThe results from the learning module as output by OLI-Torus
   """
   def __init__(self, skills, n_sessions, participants):
      self.skills = skills
      self.n_sessions = n_sessions
      self.participants = participants
      self.full_results = None
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
      for skill in self.skills:
         participant.correct_first_try[skill.name] = np.nan * np.zeros(self.n_sessions)
      
      correct_participant = self.full_results[self.full_results['Student ID'] == participant.ID]
      for skill in self.skills:
         try:
            correct_skill = correct_participant[correct_participant['Activity Title'] == skill.name]
            got_it = correct_skill["Correct?"][correct_skill["Attempt Number"] == 1].to_numpy()[0]
         except IndexError:
            got_it = False
         participant.correct_first_try.loc[0, skill.name] = got_it #This is a temporary solution until we know if multiple sessions come within one or many tsv files
      return
      
   def read_participants_results(self):
      """
      Find out, for each question, whether the participants got it right on
      the first try.
      """
      # If you simply test "[...] == None" Pandas will complain that
      # dataframes have ambiguous equality.
      if type(self.full_results) == type(None):
         print('No results have been read!')
         return
      for participant in self.participants:
         self._read_participant_results(participant)
      return
      
   def flag_participants(self):
      """
      Divide the participants into the three categories:
       1. Finished learning module
       2. Started doing learning module
       3. Signed up for learning module but has not yet answered a single
          question
      This is partly for our internal bookkeeping, but also so that we can
      send out reminders to participants who have yet to finish the module.
      """
      pass
      return
      
   def export_results(self):
      """
      This method will need to be implemented. It should export the results
      in the form of a json file, which can be read by the
      factorial_experiment module.
      """
      pass
      return
