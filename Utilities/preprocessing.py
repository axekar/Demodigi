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
import json
import matplotlib.pyplot as plt
import datetime

# This is the format that I have inferred that OLI-Torus uses for dates
_date_format = "%B %d, %Y at %I:%M %p UTC"


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
      """
      Parameters
      ----------
      name : string
      \tDescribed under attributes
      """
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
   answered : pandas DataFrame
   \tInitially empty DataFrame stating for each question in a learning
   \tmodule whether the participant has given any answer
   answer_dates : pandas DataFrame
   \tInitially empty DataFrame stating for each question in a learning
   \tmodule when the participant gave their first answer
   correct_first_try : pandas DataFrame
   \tInitially empty DataFrame stating for each question in a learning
   \tmodule whether the participant answered correctly on the first try.
   """
   def __init__(self, ID):
      """
      Parameters
      ----------
      ID : string
      \tDescribed under attributes
      """
      self.ID = ID
      self.answered = pd.DataFrame()
      self.answer_date = pd.DataFrame()
      self.correct_first_try = pd.DataFrame()
      return

   def export_results(self, folder_path):
      """
      This method will need to be implemented. It should export the results
      in the form of a json file, which can be read by the
      factorial_experiment module.
      """
      if folder_path[-1] != '/':
         folder_path += '/'
      f = open(folder_path + self.ID + '.json', 'w')
      # Here we do a weird thing because json can handle Python's built-in
      # bool type but not numpy's bool_ type.
      packed = json.dumps({'ID':self.ID, 'Number of sessions':self.n_sessions(), 'Number of skills tested':self.n_skills(), 'Results':np.array(self.correct_first_try.to_numpy().tolist(), dtype=bool).tolist()})
      f.write(packed)
      f.close()
      return

   def n_sessions(self):
      return self.correct_first_try.shape[0]

   def n_skills(self):
      return self.correct_first_try.shape[1]

   def plot_results_by_session(self, folder_path):
      """
      This plots the results for the participant as a function of session,
      showing both which number of skills they have answered, and for what
      number they answered correctly on the first try.
      """
      if folder_path[-1] != '/':
         folder_path += '/'
      plt.clf()
      plt.tight_layout()
      plt.plot(self.answered.index, self.answered.sum(1), label = 'Besvarade')
      plt.plot(self.answered.index, self.correct_first_try.sum(1), label = 'Rätt på första försöket')
      plt.legend()
      plt.xlim(1, self.n_sessions())
      plt.ylim(0, self.n_skills())
      plt.xticks(range(1, self.n_sessions()))
      plt.savefig('{}{}_resultat_per_session.png'.format(folder_path, self.ID))
      return

   def plot_results_by_time(self, folder_path):
      """
      This plots the number of answers given as a function of time.
      """
      if folder_path[-1] != '/':
         folder_path += '/'
      pass
      return
         
class learning_module:
   """
   This represents one learning module in the project.
  
   Attributes
   ----------
   skills : list of skill
   \tA list of the skills that the learning module aims to teach
   n_skills : int
   \tThe number of skills in the learning module
   n_sessions : int
   \tThe number of sessions in the learning module. The assumption is that
   \tin each session each skill will be tested once
   participants : dict of participant or None
   \tA list of the people taking the learning module, as identified in the
   \t"Student ID" column in the output from OLI-Torus. If None is given,
   \tthe participants must be read from 
   full_results : pandas DataFrame
   \tThe results from the learning module as output by OLI-Torus
   results_read : bool
   \tWhether results have been read from a file
   participants_input : bool
   \tWhether a list of participants has been provided, either when 
   \tinstantiating the learning_module or afterwards from the
   \tfull_results
   flags : pandas DataFrame
   \tFlags that note whether each participant has:
   \t1. Started the learning module (we cannot currently test this, so always set to true)
   \t2. Answered at least one question
   \t3. Finished the learning module
   """
   def __init__(self, skills, n_sessions, participants = None):
      """
      Parameters
      ----------
      skills : list of skill
      \tDescribed under attributes
      n_sessions : int
      \tDescribed under attributes
      
      Optional parameters
      -------------------
      participants : dict of participant or None
      """
      self.skills = skills
      self.n_skills = len(self.skills)
      self.n_sessions = n_sessions
      self.participants = participants
      if participants == None:
         self.participants_input = False
         self.n_participants = np.nan
      else:
         self.participants_input = True
         self.n_participants = len(participants)
      self.flags = pd.DataFrame()
      self.full_results = None
      self.results_read = False
      self.answers_by_time = pd.DataFrame()
      return

   ### Functions for inspecting data

   def describe_participants(self):
      if not self.participants_input:
         print('No participants have been read!')
      else:
         print('Participants in study are:')
         for ID, participant in sorted(self.participants.items()):
            if self.results_read:
               if self.flags.loc[ID, 'finished']:
                  status_string = 'Has finished module'
               elif self.flags.loc[ID, 'answered once']:
                  status_string = 'Has started work'
               elif self.flags.loc[ID, 'started']:
                  status_string = 'Has signed up'
               else:
                  status_string = 'Has not signed up'
            else:
               status_string = 'No results known'
            print('   {}: {}'.format(ID, status_string))
      return
      
   def plot_results(self, folder_path):
      for participant in self.participants.values():
         participant.plot_results_by_session(folder_path)
      return

   ### Functions for inputting and outputting results

   def import_oli_results(self, filepath):
      """
      Import a file with the raw statistics directly out of OLI-Torus, in the
      tab-separated values format.
      """
      raw = pd.read_csv(filepath, sep='\t')
      self.full_results = raw.astype({"Student ID": str}) # This sometimes gets interpreted as int
      self.results_read = True
      return
   
   def _read_participant_results(self, participant):
      """
      Find out, for each question, whether a specific participant got it
      right on the first try.
      """
      # This is not neat, and I will probably rewrite it at some point
      skill_names = []
      for skill in self.skills:
         skill_names.append(skill.name)
      participant.answered = pd.DataFrame(columns = skill_names, index = range(1, self.n_sessions + 1), dtype = bool)
      participant.answer_date = pd.DataFrame(columns = skill_names, index = range(1, self.n_sessions + 1), dtype = 'datetime64[m]')
      participant.correct_first_try = pd.DataFrame(columns = skill_names, index = range(1, self.n_sessions + 1), dtype = bool)
      correct_participant = self.full_results[self.full_results['Student ID'] == participant.ID]
      n_answers = 0
      for skill in self.skills:
         for session in range(1, self.n_sessions + 1):
            try:
               correct_skill = correct_participant[correct_participant['Activity Title'] == "{}_Q{}".format(skill.name, session)]
               first_try_index = correct_skill["Attempt Number"] == 1
               first_try_date_string = correct_skill["Date Created"][first_try_index].to_numpy()[0]
               first_try_date = datetime.datetime.strptime(first_try_date_string, _date_format)
               has_answered = True
               correct = correct_skill["Correct?"][first_try_index].to_numpy()[0]
               n_answers += 1
            except IndexError:
               has_answered = False
               correct = False
               first_try_date = None
            participant.answered.loc[session, skill.name] = has_answered
            participant.correct_first_try.loc[session, skill.name] = correct
            participant.answer_date.loc[session, skill.name] = first_try_date
      self.flags.loc[participant.ID, 'started'] = True # Note that this is assumed by default, we cannot test it yet
      self.flags.loc[participant.ID, 'answered once'] = n_answers > 0
      self.flags.loc[participant.ID, 'finished'] = n_answers == self.n_sessions * self.n_skills
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
      for participant in self.participants.values():
         self._read_participant_results(participant)
      return

   def export_results(self, folder_path):
      if not self.results_read:
         print('There are no results to save!')
      else:
         for participant in self.participants.values():
            participant.export_results(folder_path)
      return
      
   def infer_participants_from_full_results(self):
      """
      Figure out who the participants are from a file of results.
      """
      if not self.results_read:
         print("Must read a file of results first!")
      else:
         inferred_participant_IDs = set(self.full_results['Student ID'])
         self.participants = {}
         for ID in inferred_participant_IDs:
            self.participants[ID] = participant(ID)
      self.n_participants = len(self.participants)
      self.participants_input = True
      return
