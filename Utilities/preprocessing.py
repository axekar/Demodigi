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
import xml.etree.ElementTree as et

plt.style.use('tableau-colorblind10')

# This is the format that I have inferred that OLI-Torus uses in the raw_analytics file
_raw_date_format = "%B %d, %Y at %I:%M %p UTC"
_xml_date_format = "%Y-%m-%d %H:%M:%S"

class participant:
   """
   This represents a single person taking a learning module.
   
   Attributes
   ----------
   ID : string
   \tSome unique identifier of the participant. For privacy reasons, this
   \tis unlikely to be their actual name.
   answered : pandas bool DataFrame
   \tInitially empty DataFrame stating for each question in a learning
   \tmodule whether the participant has given any answer
   answer_dates : pandas datetime DataFrame
   \tInitially empty DataFrame stating for each question in a learning
   \tmodule when the participant gave their first answer
   first_answer_date : datetime
   \tWhen the participant first gave any answer to a question
   last_answer_date : datetime
   \tWhen the participant last gave any answer to a question
   correct_first_try : pandas bool DataFrame
   \tInitially empty DataFrame stating for each question in a learning
   \tmodule whether the participant answered correctly on the first try.
   accumulated_by_date : dict
   \tInitially empty dict given the number of questions answered as a
   \tfunction of time.
   """
   def __init__(self, ID):
      """
      Parameters
      ----------
      ID : string
      \tDescribed under attributes
      """
      self.ID = ID
      self.answered = pd.DataFrame(dtype = bool)
      self.answer_date = pd.DataFrame(dtype = 'datetime64[s]')
      self.first_answer_date = None
      self.last_answer_date = None
      self.correct_first_try = pd.DataFrame(dtype = bool)
      # I would *like* to implement this one as a DataFrame, but it turns
      # out that Pandas does not accept datetime64 objects.
      self.accumulated_by_date = {}
      return

   def save_factorial_experiment_data(self, folder_path):
      """
      Save data that will be used by the factorial_experiment module.
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
      
   def _cumulative_answers_by_date(self):
      dates_when_something_happened = {}
      for date in self.answer_date.values.flatten():
         if not np.isnan(date):
            if not (date in dates_when_something_happened.keys()):
               dates_when_something_happened[date] = 1
            else:
               dates_when_something_happened[date] += 1
      accumulated = 0
      accumulated_by_date = {}
      for date in sorted(dates_when_something_happened.keys()):
         accumulated += dates_when_something_happened[date]
         accumulated_by_date[date] = accumulated
      self.accumulated_by_date = accumulated_by_date
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
      plt.plot(self.answered.index, self.answered.sum(1), label = 'Besvarade frågor')
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
      # Avoid plotting if there is nothing to plot.
      if self.accumulated_by_date == {}:
         return
      
      if folder_path[-1] != '/':
         folder_path += '/'
      plt.clf()
     
      sorted_dates_accumulated = list(zip(*sorted(zip(self.accumulated_by_date.keys(), self.accumulated_by_date.values()))))
      plt.plot(sorted_dates_accumulated[0], sorted_dates_accumulated[1], 'o-', label = 'Besvarade frågor')
      plt.legend()
      plt.ylim(0, self.n_sessions() * self.n_skills())
      plt.xticks(rotation = 90)
      plt.tight_layout()
      plt.savefig('{}{}_resultat_över_tid.png'.format(folder_path, self.ID))
      return
         
class learning_module:
   """
   This represents one learning module in the project.
  
   Attributes
   ----------
   skills : list of str
   \tA list of the skills that the learning module aims to teach
   n_skills : int
   \tThe number of skills in the learning module
   n_sessions : int
   \tThe number of sessions in the learning module. The assumption is that
   \tin each session each skill will be tested once. If nan is given, the
   \tnumber of sessions must be inferred from the OLI-Torus output.
   n_sessions_input : bool
   \tWhether a number of sessions has been supplied
   participants : dict of participant or None
   \tA list of the people taking the learning module, as identified in the
   \t"Student ID" column in the output from OLI-Torus. If None is given,
   \tthe participants must be inferred from the OLI-Torus output.
   participants_input : bool
   \tWhether a list of participants has been provided, either when 
   \tinstantiating the learning_module or afterwards from the
   n_participants : int
   \tThe number of participants
   full_results : pandas DataFrame
   \tThe results from the learning module as output by OLI-Torus
   results_read : bool
   \tWhether results have been read from a file
   date_format : str
   \tThe date format used in the file that results are imported from
   flags : pandas DataFrame
   \tFlags that note whether each participant has:
   \t1. Started the learning module (we cannot currently test this, so always set to true)
   \t2. Answered at least one question
   \t3. Finished the learning module
   accumulated_by_date : dict
   \tInitially empty dict given the number of questions answered as a
   \tfunction of time.
   """
   def __init__(self, skills, n_sessions = np.nan, participants = None):
      """
      Parameters
      ----------
      skills : list of str
      \tDescribed under attributes
      
      Optional parameters
      -------------------
      n_sessions : int
      \tDescribed under attributes
      participants : dict of participant or None
      \tDescribed under attributes
      """
      self.skills = skills
      self.n_skills = len(self.skills)
      self.n_sessions = n_sessions
      self.n_sessions_input = np.isfinite(self.n_sessions)
      self.participants = participants
      if self.participants == None:
         self.participants_input = False
         self.n_participants = np.nan
      else:
         self.participants_input = True
         self.n_participants = len(participants)
      self.flags = pd.DataFrame()
      self.raw_analytics = None
      self.full_results = None
      self.results_read = False
      self.date_format = ''
      self.accumulated_by_date = {}
      return

   ### Functions for handling data regarding individual participants

   def read_participant_IDs(self, filepath):
      """
      Reads a list of the participant IDs. The file is assumed to consist of
      a single column of IDs.
      
      The file of IDs is assumed to have been generated by the
      account_info_generator module.
      """
      f = open(filepath)
      IDs = [word.strip().lower() for word in f]
      f.close()
      self.participants = {}
      for ID in IDs:
         self.participants[ID] = participant(ID) 
      return

   def import_raw_analytics(self, filepath, section_slug = None):
      """
      Import the raw_analytics.tsv file given by OLI Torus and pick out the 
      relevant information.
      
      Specifying section_slug means that only results matching the column
      "Section Slug" in the OLI Torus file get picked.
      """
      raw = pd.read_csv(filepath, sep='\t')
      cleaned = raw.astype({"Student ID": str}) # This sometimes gets interpreted as int
      if section_slug != None:
         cleaned = cleaned[cleaned['Section Slug'] == section_slug]
      self.raw_analytics = cleaned
      
      self.full_results = pd.DataFrame(data={'Student ID':self.raw_analytics['Student ID'], "Date Created":self.raw_analytics["Date Created"], 'Activity Title': self.raw_analytics['Activity Title'],"Attempt Number": self.raw_analytics["Attempt Number"],"Correct?": self.raw_analytics["Correct?"]})
      self.results_read = True
      self.date_format = _raw_date_format
      return
      
      
   def import_datashop(self, filepath):
      """
      This imports an XML file following the format specified at
      
      https://pslcdatashop.web.cmu.edu/dtd/guide/tutor_message_dtd_guide_v4.pdf
      
      The assumption is that for each problem there will be a context_message
      followed by one or more pairs of first tool_message and tutor_message.
      Internally, these are ordered in time, but the whole batch of context,
      tool and tutor messages need not be ordered with respect to others.
      """

      tree = et.parse(filepath)
      root = tree.getroot()
      
      # We make a first run to pick out the relevant information and store it
      # in a way that will allow us to pick out the attempt number.
      answers = {}
      
      # Some questions do not match the standard format for problems in the
      # XML file. They should simply be ignored.
      wait_for_next_context_message = False
      
      for child in root:
         if child.tag == 'context_message':
            meta = child.findall('meta')[0]
            anon_id = meta.findall('user_id')[0].text
            time = meta.findall('time')[0].text
            
            try:
               full_problem_name = child.findall('dataset')[0].findall('level')[0].findall('level')[0].findall('problem')[0].findall('name')[0].text
            except IndexError:
               wait_for_next_context_message = True
               continue
            wait_for_next_context_message = False
            
            problem_name = full_problem_name.split(' ')[1][:-1]

            if not (anon_id in answers.keys()):
               answers[anon_id] = {}
            if not (problem_name in answers[anon_id].keys()):
               answers[anon_id][problem_name] = {}
            answers[anon_id][problem_name][time] = []
               
         elif child.tag == 'tool_message' and (not wait_for_next_context_message):
            pass
         elif child.tag == 'tutor_message' and (not wait_for_next_context_message):
            action_eval = child.findall('action_evaluation')[0].text
            answers[anon_id][problem_name][time].append(action_eval == 'CORRECT')
      
      
      # We now put the information in a pandas dataframe
      IDs = []
      answer_dates = []
      correct = []
      activity_titles = []
      attempt_number = []
      for anon_id, problem in answers.items():
        
         for problem_name, times in problem.items():
            # Remove those problems that do not match any skill that we are
            # trying to test, such as practise problems, feedback, etc
            matched_skill = False
            for skill in self.skills:
               for session in range(self.n_sessions):
                  mixedcase_name = '{}_Q{}'.format(skill, session)
                  if problem_name == mixedcase_name.lower():
                     matched_skill = True
            if not matched_skill:
               continue
               
            i = 1
            for time, answers in sorted(times.items()):
               for is_correct in answers:
                  IDs.append(anon_id)
                  activity_titles.append(mixedcase_name)
                  correct.append(is_correct)
                  answer_dates.append(time)
                  attempt_number.append(i)
                  i += 1

      self.full_results = pd.DataFrame(data={'Student ID':IDs, "Date Created":answer_dates, 'Activity Title': activity_titles,"Attempt Number": attempt_number,"Correct?": correct})
      self.results_read = True
      self.date_format = _xml_date_format
      return
      
   def _read_participant_results(self, participant):
      """
      Find out, for each question, whether a specific participant got it
      right on the first try.
      """
      if not self.n_sessions_input:
         print('Inferring number of sessions from OLI-Torus output')
         self.infer_n_sessions_from_full_results()

      participant.answered = pd.DataFrame(columns = self.skills, index = range(1, self.n_sessions + 1), dtype = bool)
      participant.answer_date = pd.DataFrame(columns = self.skills, index = range(1, self.n_sessions + 1), dtype = 'datetime64[s]')
      participant.correct_first_try = pd.DataFrame(columns = self.skills, index = range(1, self.n_sessions + 1), dtype = bool)
      correct_participant = self.full_results[self.full_results['Student ID'] == participant.ID]
      n_answers = 0
      participant.first_answer_date = datetime.datetime.max
      participant.last_answer_date = datetime.datetime.min
      for skill in self.skills:
         for session in range(1, self.n_sessions + 1):
            try:
               correct_skill = correct_participant[correct_participant['Activity Title'] == "{}_Q{}".format(skill, session)]
               first_try_index = correct_skill["Attempt Number"] == 1
               first_try_date_string = correct_skill["Date Created"][first_try_index].to_numpy()[0]
               first_try_date = datetime.datetime.strptime(first_try_date_string, self.date_format)
               has_answered = True
               correct = correct_skill["Correct?"][first_try_index].to_numpy()[0]
               n_answers += 1
               if first_try_date < participant.first_answer_date:
                  participant.first_answer_date = first_try_date
               if first_try_date > participant.last_answer_date:
                  participant.last_answer_date = first_try_date
            except IndexError:
               has_answered = False
               correct = False
               first_try_date = None
            participant.answered.loc[session, skill] = has_answered
            participant.correct_first_try.loc[session, skill] = correct
            participant.answer_date.loc[session, skill] = first_try_date
      participant._cumulative_answers_by_date()
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
      self.accumulated_by_date = self._cumulative_answers_by_date(self.participants.values())
      return

   def export_full_results(self, file_path):
      """
      Export the full results dataframe as a csv file.
      
      This is mostly intended to make visual inspection easier.
      """
      self.full_results.to_csv(file_path, index = False)
      return

   def export_results(self, folder_path):
      """
      Export the results for each individual participant in a format which is
      legible to the factorial_experiment module.
      """
      if not self.results_read:
         print('There are no results to save!')
      else:
         for participant in self.participants.values():
            participant.save_factorial_experiment_data(folder_path)
      return

   def export_IDs(self, file_path):
      """
      Write a file of participant IDs, which can be read by the
      factorial_experiment module, or by this module.
      
      There should not be any need to use this function, except when
      participants have been inferred from the results file.
      """
      f = open(file_path, 'w')
      # Here we do a weird thing because json can handle Python's built-in
      # bool type but not numpy's bool_ type.
      packed = json.dumps({'IDs':list(self.participants.keys())})
      f.write(packed)
      f.close()
      return      

   def export_SCB_data(self, file_path):
      """
      Write a csv file to be delivered to Statistiska Centralbyrån (SCB), which
      contains the columns:
      
      person number, estimated time, starting date, finishing date
      
      The estimated time is always given as 30 minutes.
      """
      sorted_IDs = sorted(self.participants.keys())
      first_answer_dates = []
      last_answer_dates = []
      for ID in sorted_IDs:
         first_answer_dates.append(self.participants[ID].first_answer_date.date())
         if self.flags.loc[ID, 'finished']:
            last_answer_dates.append(self.participants[ID].last_answer_date.date())
         else:
            last_answer_dates.append('Ej klar')

      SCB_data = pd.DataFrame(columns = ['Personnummer', 'Uppskattad tid', 'Startdatum', 'Avslutsdatum'])
      SCB_data['Startdatum'] = first_answer_dates
      SCB_data['Avslutsdatum'] = last_answer_dates
      SCB_data['Personnummer'] = 'Ej känt'
      SCB_data['Uppskattad tid'] = '30 min'
      SCB_data.to_csv(file_path, index = False)
      return

   ### Functions for handling data regarding groups of participants
   
   def _cumulative_answers_by_date(self, participants):
      dates_when_something_happened = {}
      for participant in participants:
         for date in participant.answer_date.values.flatten():
            if not np.isnan(date):
               if not (date in dates_when_something_happened.keys()):
                  dates_when_something_happened[date] = 1
               else:
                  dates_when_something_happened[date] += 1
      accumulated = 0
      accumulated_by_date = {}
      for date in sorted(dates_when_something_happened.keys()):
         accumulated += dates_when_something_happened[date]
         accumulated_by_date[date] = accumulated
      return accumulated_by_date
   
      ### Functions for inspecting data

   def describe_participants(self):
      """
      Give a short summary of who the participants are and how far they have
      gotten in the course.
      """
      if not self.participants_input:
         print('No participants have been read!')
      else:
         print('There are {} participants:'.format(len(self.participants)))
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
      
   def plot_individual_results(self, folder_path):
      """
      Plot the results for each individual participant.
      """
      for participant in self.participants.values():
         participant.plot_results_by_session(folder_path)
         participant.plot_results_by_time(folder_path)
      return

   def plot_results_by_time(self, folder_path):
      """
      This plots the number of answers given as a function of time.
      """
      if folder_path[-1] != '/':
         folder_path += '/'
      plt.clf()
     
      sorted_dates_accumulated = list(zip(*sorted(zip(self.accumulated_by_date.keys(), self.accumulated_by_date.values()))))
      plt.plot(sorted_dates_accumulated[0], sorted_dates_accumulated[1], '-', label = 'Besvarade frågor')
      plt.legend()
      plt.ylim(0, self.n_sessions * self.n_skills * self.n_participants)
      plt.xticks(rotation = 90)
      plt.tight_layout()
      plt.savefig('{}Resultat_över_tid.png'.format(folder_path))
      return

   def plot_results(self, folder_path):
      """
      This plots everything that can be plotted
      """
      self.plot_individual_results(folder_path)
      self.plot_results_by_time(folder_path)
      return
   
   ### Function for inferring parameters when they are not available
   ### (as a rule, you should not need to use these unless something has
   ### gone wrong)
   
   def infer_participants_from_full_results(self):
      """
      Figure out who the participants are from a file of results.
      
      NOTE: You should never actually need to use this
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
      
   def infer_n_sessions_from_full_results(self, verbose = False):
      """
      Figure out how many sessions there are from a file of results.
      
      NOTE: You should never actually need to use this
      """
      if not self.results_read:
         print("Must read a file of results first!")
      else:
         n_sessions = {}
         for skill in self.skills:
            n_sessions[skill] = 0
            activities = self.full_results['Activity Title'].to_numpy()
            while "{}_Q{}".format(skill, n_sessions[skill] + 1) in activities:
               n_sessions[skill] += 1
      if verbose:
         print('Number of sessions registered:')
         for skill_name, n in n_sessions.items():
            print('{}: {}'.format(skill_name, n))
               
      self.n_sessions = max(n_sessions.values())
      self.n_sessions_input = True
      return
