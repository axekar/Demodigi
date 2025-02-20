"""
This module was written for the ESF-financed project Demokratisk
Digitalisering. The project is a collaboration between
Arbetsförmedlingen (AF) and Kungliga Tekniska Högskolan (KTH). The
purpose of the project is to increase the digital competence - as
defined at https://ec.europa.eu/jrc/en/digcomp - of people working at
Arbetsförmedlingen, and by extension also job seekers. This will be
done by learning modules at KTH using OLI-Torus.

--- About the learning modules ---

Each learning module is supposed to teach some broadly-defined area,
such as IT security. This area is divided into a certain number of
skills. When taking a learning module, the participant is each session
given one question for each skill. Whatever answer they give they get
detailed feedback, and they get to try over and over again until they
get the answer right. From our point of view the ideal is that the
participants should answer every question wrong on the first try on the
first session, and immediately get the questions testing the same skill
right on the subsequent sessions. This would mean that they did not
already know any of what we wanted to teach them, but that they picked
it up quickly and were able to recollect it afterwards.

--- About this Python module ---

This module can be used to analyse either real or simulated data. The
latter is intended as a proof-of-concept, to ensure that the planned
analysis makes sense before we have seen real data.

Behind the scenes we model the digital competence of a participant as a
real number between 0 and 1, which gives the probability of giving the
correct answer to a summative question in one of the learning modules.
However, this number is not accessible to the experimentalists. All
they see is the actual number of correct answers.

The study is assumed to use a factorial design, so that the experiment-
ers first identify some binary background variables (BBV) - such as 
whether the participant's native language is the same as the language
of the learning module - and split the participants into several
smaller groups within which all members are affected the same. They
then try out a certain number of changes in the course - here referred
to as 'manipulations'. To evaluate the effect of the manipulations the
participant groups are further halved ortogonally, so that with 
n manipulations each group affected identically by BBVs is split into
2^n subgroups that each get some combination of manipulations.

Written by Alvin Gavel,

https://github.com/Alvin-Gavel/Demodigi
"""
import os
from abc import ABC, abstractmethod
import numbers as nb
import json

import numpy as np
import numpy.random as rd
import scipy.special as sp
import scipy.stats as st
import matplotlib.pyplot as plt


### Tools for inspecting data

def read_nested_dict(dictionary):
   """
   In this module a lot of data is stored as nested dicts. This tool is
   intended to make it easier to inspect them.
   
   Given a dict, you will be shown the keys and some information about
   the corresponding values. For most data types only the type itself is
   printed out. Individual numeric values are printed out. Strings are
   printed out but shortened if too long. For lists, tuples and sets the
   length is shown. For numpy arrays the size and dtype is shown.
   
   Any dicts inside the dict can in turn be entered, permitting you to
   descend through the levels of a tree of dicts and ascend again.
   """
   def print_dict_level_contents(dict_level):
      keys = {'Other data':[]}
      values = {'Other data':[]}
      
      sorting_type_nondict_order = ['Numpy ndarray', 'Collections not dict or ndarray', 'Numerical', 'String', 'Other data']
      sorting_types = {'Dictionary':[dict], 'String':[str], 'Collections not dict or ndarray':[list, set, tuple], 'Numpy ndarray':[np.ndarray], 'Numerical':[nb.Number]}
      for sorting_type_name, sorting_type_list in sorting_types.items():
         keys[sorting_type_name] = []
         values[sorting_type_name] = []
      
      for key, value in dict_level.items():
         found_type = False
         for sorting_type_name, sorting_type_list in sorting_types.items():
            for sorting_type in sorting_type_list:
               if isinstance(value, sorting_type):
                  keys[sorting_type_name].append(key)
                  values[sorting_type_name].append(value)
                  found_type = True
         if not found_type:
            keys['Other data'].append(key)
            values['Other data'].append(value)
   
      n = {}
      for sorting_type_name in list(sorting_types.keys()) + ['Other data']:
         n[sorting_type_name] = len(keys[sorting_type_name])
   
      print("Dictionaries:")
      if dict_level != dictionary:
         print("{}0: (Go up one level)".format(_indent(1)))
      if n['Dictionary'] > 0:
         dict_keys, dicts = zip(*sorted(zip(keys['Dictionary'], values['Dictionary'])))
         for i in range(n['Dictionary']):
            print("{}{}: {}".format(_indent(1), i+1, keys['Dictionary'][i]))
      print("{}q: (Leave nested dict)".format(_indent(1)))
         
      for sorting_type_name in sorting_type_nondict_order:
         if n[sorting_type_name] > 0:
            print("{}:".format(sorting_type_name))
            sorted_keys, sorted_values = zip(*sorted(zip(keys[sorting_type_name], values[sorting_type_name])))
            for i in range(n[sorting_type_name]):
               if sorting_type_name == 'Numpy ndarray':
                  print("{}{}".format(_indent(1), sorted_keys[i]))
                  print("{}Type: {}".format(_indent(2), sorted_values[i].dtype))
                  print("{}Size: {}".format(_indent(2), sorted_values[i].size))
               elif sorting_type_name == 'Collections not dict or ndarray':
                  print("{}{}".format(_indent(1), sorted_keys[i]))
                  print("{}Size: {}".format(_indent(2), len(sorted_values[i])))
               elif sorting_type_name in ['Numerical', 'String']:
                  print("{}{}".format(_indent(1), sorted_keys[i]))
                  print("{}Value: {}".format(_indent(2), sorted_values[i]))
               else:
                  print("{}{}".format(_indent(1), sorted_keys[i]))
                  print("{}Type: {}".format(_indent(2), type(sorted_values[i])))
      choice = input("Type in choice:\n")
      print("\n")
      return keys["Dictionary"], choice

   current_level = dictionary
   higher_levels = []
   level_names = []
   choice = 'dummy'
   while choice != 'q':
      if level_names != []:
         print("In sub-dictionary '{}'".format(level_names[-1]))
      dict_keys, choice = print_dict_level_contents(current_level)
      try:
         choice_int = int(choice)
         if choice_int == 0:
            if higher_levels == []:
               print("Already at highest level of nested dictionary")
            else:
               current_level = higher_levels.pop()
               level_names.pop()
         elif choice_int < 0 or choice_int > len(dict_keys):
            print("Choice {} not in range of options".format(choice_int))
         else:
            choice_key = dict_keys[choice_int - 1]
            higher_levels.append(current_level)
            level_names.append(choice_key)
            current_level = current_level[choice_key]
      except ValueError:
         if choice != 'q':
            print("Could not parse input {}".format(choice))
   return


### Internal functions for handling text

def _trim_for_filename(string):
   """
   Removes parts of a string that would not be suitable for a filename
   """
   for character in ['\\', '"', '*' '/', '>', '<', '|', ':', ';', '&', '?', '.']:
      string = string.replace(character, '')
   for character in [' ', ',']:
      string = string.replace(character, '_')      
   return string

def _is_are(n):
   word = "is" if n == 1 else "are" 
   return word

def _plural_ending(n):
   ending = "" if n == 1 else "s" 
   return ending
   
def _initial_capital(string):
   return string[0].upper() + string[1:]

def _indent(n):
   return n * '   '

def _trim_comments(lines):
   """
   Takes a list of strings and removes anything to the right of a '#'.
   Leading and trailing whitespace is also removed. If a string begins
   with '#', that string is removed entirely from the list.
   """
   trimmed = []
   for line in lines:
      try:
         comment_position = line.index('#')
         trimmed_line = line[:comment_position].strip()
         if trimmed_line != '':
            trimmed.append(trimmed_line)
      except ValueError:
         trimmed.append(line.strip())
   return trimmed


### Misc. stuff

def _define_subgroups(n, BBVs_or_manipulations, BBV_or_manipulation_flags):
   """
   Take a list of manipulations or BBVs, together with a list of
   boolean flags stating which participants are affected, and create
   arrays with the indices of those that are affected by the manipulation
   or BBV in question.
   """
   groups = {}
   group_names = set([])
   for i in range(n):
      flags = []
      for BBV_or_manipulation in BBVs_or_manipulations:
          if BBV_or_manipulation_flags[BBV_or_manipulation.name][i]:
             flags.append(BBV_or_manipulation.name)
      group_name = ", ".join(flags)
      if group_name == "":
         group_name = "none"
      if not (group_name in group_names):
         groups[group_name] = []
         group_names.add(group_name)
      groups[group_name].append(i)
   for group_name in group_names:
      groups[group_name] = np.asarray(groups[group_name])
   return groups

def ordinalise(ndarray):
   """
   Takes a 1-d ndarray and makes the data ordinal. That is to say, the
   elements will be turned into integers denoting the lowest, second
   lowest, etcetera.
   """
   n = len(ndarray)
   ordinal = np.zeros(n, dtype=np.int64)
   sorted_array = np.unique(ndarray)

   i = 0
   j = 0 # Just in case somebody feeds this some really weird data
   while i < n and j < n:
      element = ndarray[i]
      for index in np.where(sorted_array == element)[0]:
         ordinal[i] = index
         i += 1
      j += 1
   return ordinal
   
def ordinalise_many(ndarrays):
   """
   Takes a list of ndarrays and puts them on a common ordinal scale.
   """
   concatenated = np.concatenate(ndarrays)
   ordinal_long = ordinalise(concatenated)
   ordinal = []
   cut = 0
   for ndarray in ndarrays:
      length = len(ndarray)
      ordinal.append(ordinal_long[cut:cut+length])
      cut += length
   return ordinal
   
def logB(alpha, beta):
   """
   The logarithm of the normalisation factor that appears when doing
   Bayesian fitting of binomial functions.
   """
   return sp.loggamma(alpha) + sp.loggamma(beta) - sp.loggamma(alpha + beta)

class IDMismatchError(Exception):
   """
   Raised when reading data from a file and finding that the IDs in the
   file do not match the ones expected.
   """
   pass

def _match_ids(reference_ids, ids, data):
   if not (len(reference_ids) == len(ids) == len(data)):
      raise IDMismatchError
   if len(reference_ids) != len(set(reference_ids)):
      raise IDMismatchError
   if len(ids) != len(set(ids)):
      raise IDMismatchError

   sorted_data = ids[:]
   for ID, datum in zip(ids, data):
      try:
         sorted_data[reference_ids.index(ID)] = datum
      except ValueError:
         raise IDMismatchError
   return sorted_data
      

### Digital competence effects
# These are functions that change digital competence in some way. They
# assume that digital competence is a real number above 0 and below 1,
# corresponding to the probability of correctly answering a question in
# the learning module.

def improvement(digicomp_initial, factor):
   """
   Represents an effect which decreases the risk of incorrectly answering
   a summative question by some factor
   """
   return 1 - factor * (1 - digicomp_initial)

def deterioration(digicomp_initial, factor):
   """
   Represents an effect which increases the risk of incorrectly answering
   a summative question by some factor
   """
   return factor * digicomp_initial

standard_transformations = {"large improvement": lambda digicomp_initial : improvement(digicomp_initial, 1/2),
                            "moderate improvement": lambda digicomp_initial : improvement(digicomp_initial, 2/3),
                            "slight improvement": lambda digicomp_initial : improvement(digicomp_initial, 4/5),
                            "minimal improvement": lambda digicomp_initial : improvement(digicomp_initial, 9/10),
                            "large deterioration": lambda digicomp_initial : deterioration(digicomp_initial, 1/2),
                            "moderate deterioration": lambda digicomp_initial : deterioration(digicomp_initial, 2/3),
                            "slight deterioration": lambda digicomp_initial : deterioration(digicomp_initial, 4/5),
                            "minimal deterioration": lambda digicomp_initial : deterioration(digicomp_initial, 9/10),
                            "no effect": lambda digicomp_initial : digicomp_initial[:]}

### Classes

class manipulation(ABC):
   """
   This represents some change we make to the course, which we try out on
   a subset of the participants. This means that the participants will be
   divided into a control group and a test group, which will be as close
   to a 50/50 split as possible. Where there are known BBVs, the
   subsets sharing the same BBVs will also be split approximately
   in half.
   
   As a rule all manipulations are binary. That is, they are either done
   or not done, but there are no manipulations that we try out to varying
   degrees.
   """
   @abstractmethod
   def __init__(self, name):
      self.name = name
      self.name_for_file = _trim_for_filename(self.name)
      return
      
class simulated_manipulation(manipulation):
   """
   See base class manipulation for definition.
   
   This is used when simulating a study. It requires the user to specify a
   transformation that describes how the digital competence of the
   participants is affected by the manipulation.
   
   Attributes
   ----------
   name : str
   \tDescription of the manipulation
   name_for_file : str
   \tRendition of the name suitable for use in a file name
   transformation : function float -> float
   \tSome mapping ]0, 1[ -> ]0, 1[ representing how digital competence is
   \taffected by this manipulation
   """
   
   def __init__(self, name, transformation):
      """
      Parameters
      ----------
      name : str
      \tDescribed under attributes
      transformation : function float -> float
      \tDescribed under attributes
      """
      manipulation.__init__(self, name)
      self.transformation = transformation
      return

class real_manipulation(manipulation):
   """
   See base class manipulation for definition.
   
   This is used when performing a real study.
      
   Attributes
   ----------
   name : str
   \tDescription of the manipulation
   name_for_file : str
   \tRendition of the name suitable for use in a file name
   """
   
   def __init__(self, name):
      """
      Parameters
      ----------
      name : str
      \tDescribed under attributes
      """
      manipulation.__init__(self, name)
      return

class BV(ABC):
   """
   This represents a background variable. That is, something that can be
   expected to affect the results of the participants in the study, but
   which cannot be directly controlled by the experimenters.
   """
   @abstractmethod
   def __init__(self, name):
      self.name = name
      self.name_for_file = _trim_for_filename(self.name)
      return

class CBV(BV):
   """
   This represents a continuous background variable. For example, the age
   of the participants.
   """
   @abstractmethod
   def __init__(self, name):
      BV.__init__(self, name)
      return
      
class simulated_CBV(CBV):
   """
   See base class CBV for definition.
   
   This is used when simulating a study. It requires the user to define
   transformations that describe how the CBV affects both the
   initial digital competence and the effect of the learning module.
   
   Attributes
   ----------
   name : str
   \tDescription of the BBV
   name_for_file : str
   \tRendition of the name suitable for use in a file name
   pre_transformation : function (float, float) -> float
   \tFunction that describes the effect that the BBV has on the digital
   \tskills of a participants with a given value of the CBV, prior to
   \ttaking the learning module.
   \tNB: This must on ndarrays as well as individual floats
   post_transformation : function (float, float) -> float ndarray
   \tFunction that describes the effect that the BBV has on the digital
   \tskills of a participants with a given value of the CBV, after taking
   \tthe learning module.
   \tNB: This must on ndarrays as well as individual floats
   PDF : function int -> float ndarray
   \tFunction that given a number of participants gives assigns values
   \tof the CBV to those participants. For example, if the CBV represents
   \tage this could take random samples from the statistical distribution
   \tof age in Sweden, truncated at 18 and with some kind of drop-off at
   \tretirement age.
   """
   def __init__(self, name, pre_transformation, post_transformation, PDF):
      """
      Parameters
      ----------
      name : str
      \tDescribed under attributes
      pre_transformation : function (float, float) -> float
      \tDescribed under attributes
      post_transformation : function (float, float) -> float
      \tDescribed under attributes
      PDF : function int -> float ndarray
      \tDescribed under attributes
      """
      CBV.__init__(self, name)
      self.pre_transformation = pre_transformation
      self.post_transformation = post_transformation
      self.PDF = PDF
      return
      
class real_CBV(CBV):
   """
   See base class CBV for definition.
   
   This is used for real studies.

   Attributes
   ----------
   name : str
   \tDescription of the CBV
   name_for_file : str
   \tRendition of the name suitable for use in a file name
   """
   
   def __init__(self, name):
      """
      Parameters
      ----------
      name : str
      \tDescribed under attributes
      """
      CBV.__init__(self, name)
      return

class BBV(BV):
   """
   This represents a binary background variable. For example, whether the
   native language of the participants is the same as the language of the
   learning module.
   """
   @abstractmethod
   def __init__(self, name):
      BV.__init__(self, name)
      return
      
class simulated_BBV(BBV):
   """
   See base class BBV for definition.
   
   This is used when simulating a study. It requires the user to define
   transformations that describe how the BBV affects both the
   initial digital competence and the effect of the learning module.
   
   Some BBVs are assumed to be known ahead of time, some are discovered
   during the course of the learning module, and some remain unknown. One
   goal of these simulations is to get an idea of how much the unknown may
   interfere with our results.

   Attributes
   ----------
   name : str
   \tDescription of the BBV
   name_for_file : str
   \tRendition of the name suitable for use in a file name
   pre_transformation : function float -> float
   \tSome function ]0, 1[ -> ]0, 1[ that describes the effect that the
   \tBBV has on the digital skills of the participants prior to the
   \tstudy
   post_transformation : function float -> float
   \tSome function ]0, 1[ -> ]0, 1[ that describes the effect that the
   \tBBV has on the improvement of the digital skills of the
   \tparticipants during the course of the study
   fraction : float
   \tThe probability that a given participant is affected by the
   \tBBV
   """
   
   def __init__(self, name, pre_transformation, post_transformation, fraction):
      """
      Parameters
      ----------
      name : str
      \tDescribed under attributes
      pre_transformation : function float -> float
      \tDescribed under attributes
      post_transformation : function float -> float
      \tDescribed under attributes
      fraction : float
      \tDescribed under attributes
      """
      BBV.__init__(self, name)
      self.pre_transformation = pre_transformation
      self.post_transformation = post_transformation
      self.fraction = fraction
      return
      
class real_BBV(BBV):
   """
   See base class BBV for definition.
   
   This is used for real studies.

   Attributes
   ----------
   name : str
   \tDescription of the BBV
   name_for_file : str
   \tRendition of the name suitable for use in a file name
   """
   def __init__(self, name):
      """
      Parameters
      ----------
      name : str
      \tDescribed under attributes
      """
      BBV.__init__(self, name)
      return

class boundaries:
   """
   This is used in one possible test for evaluating the effectiveness of a
   learning module. We define two boundaries, such that participants whose   
   fraction of correct answers lie below the lower boundary are considered
   to have poor skills and those above the higher boundary have good
   skills. The boundaries can be identical, but this is probably not
   optimal, since it will likely result in modules being evaluated by
   their ability to push people from just below to just above passing.
   
   A skill_boundaries object should be given to a study object, where it
   will be used to evaluate the performance of the participants.
   
   Optionally, it is possible to also supply a minimal difference in
   quality which we consider to be practically significant.
   
   Attributes
   ----------
   poor : float
   \tThe fraction of correct answers below which participants are
   \tconsidered to have low digital competence
   good : float
   \tThe fraction of correct answers above which participants are
   \tconsidered to have high digital competence
   minimum_quality_difference : float
   \tThe difference in quality between two manipulations or BBVs
   \twhich we consider to be practically significant. This defaults to
   \tzero, meaning that any different is taken to be practically
   \tsignificant.
   """
   def __init__(self, poor, good, minimum_quality_difference = 0.):
      """
      Parameters
      ----------
      poor : float
      \tDescribed under attributes
      good : float
      \tDescribed under attributes
      
      Optional parameters
      -------------------
      minimum_quality_difference : float
      \tDescribed under attributes
      """
      if poor > good:
         raise ValueError("Poor results are higher than good!")
      if good > 1.0:
         raise ValueError("It is not possible to have more than 100% correct results")
      if poor < 0.0:
         raise ValueError("It is not possible to have less than 0% correct results")
      self.poor = poor
      self.good = good
      self.minimum_quality_difference = minimum_quality_difference
      return


class participant(ABC):
   """
   This represents a single person taking a learning module.
   
   Attributes
   ----------
   ID : string
   \tSome unique identifier of the participant. For privacy reasons, this
   \tis unlikely to be their actual name.
   n_sessions : int
   \tThe number of sessions that the participant has participated in
   n_skills : int
   \tThe number of separate skills that the participant has been tested on
   results_read : bool
   \tWhether any results have been set for the participant, either by
   \tactual data being read from a file or simulated data being calculated
   
   Attributes set by load_results or calculate_results
   ---------------------------------------------------
   results : bool ndarray
   \tArray stating whether the first answer attempt was correct for each
   \tskill during each session. The first index denotes skill, the second
   \tdenotes session
   last_wrong : int ndarray of length n_skills
   \tBy which session the participant last answered wrong on the first try
   \ton the questions testing each particular skill. Negative one should
   \tbe taken to mean that they got it right on the first try.
   correct_onwards : int ndarray of length n_sessions
   \tFor each session, how many skills got correct answers from that
   \tsession onwards
   """
   def __init__(self, ID):
      """
      This simply sets some dummy values which must be defined by the
      inheriting classes.
      """
      self.ID = ID
      self.n_sessions = np.nan
      self.n_skills = np.nan
      self.results = np.asarray([], dtype = bool)
      self.results_read = False
      self.last_wrong = np.asarray([], dtype = np.int64)
      self.correct_onwards = np.asarray([], dtype = np.int64)
      return

   def _evaluate_results_according_to_last_wrong(self):
      """
      Evaluate the quality of the participants' results by looking at from
      which session onwards they consistently answered the questions on a
      particular skill correctly
      """
      def last_wrong_per_skill(skill_row):
         column = self.n_sessions - 1
         while skill_row[column] and column >= 0:
            column -= 1
         return column
         
      if not self.results_read:
         print('No results to evaluate')
         return
      self.last_wrong = np.zeros(self.n_skills, dtype = np.int64)
      for i in range(self.n_skills):
         self.last_wrong[i] = last_wrong_per_skill(self.results[:,i]) # Replace this w. something neater. I'm pretty sure you could just use index

      self.correct_onwards = np.zeros(self.n_sessions, dtype = np.int64)      
      for i in range(self.n_sessions):
         self.correct_onwards[i] = np.sum(self.last_wrong < i)
      return
   
   def save_results(self, folder_path):
      """
      Save a file listing the first answer attempts to each question
      This requires a path to a folder, where a file with the name of
      """
      if folder_path[-1] != '/':
         folder_path += '/'
      f = open(folder_path + self.ID + '.json', 'w')
      packed = json.dumps({'ID':self.ID, 'Number of sessions':self.n_sessions, 'Number of skills tested': self.n_skills, 'Results':self.results.tolist()})
      f.write(packed)
      f.close()
      return
      
   def load_results(self, folder_path):
      """
      Load the results from a folder, which has to contain a file with a
      filename following the format [participant ID].json
      """
      if folder_path[-1] != '/':
         folder_path += '/'
      f = open(folder_path + self.ID + '.json', 'r')
      packed = f.read()
      f.close()
      unpacked = json.loads(packed)
      self.n_sessions = unpacked['Number of sessions']
      self.n_skills = unpacked['Number of skills tested']
      self.results = np.asarray(unpacked['Results'], dtype = bool)
      self.results_read = True
      self._evaluate_results_according_to_last_wrong()
      return


class real_participant(participant):
   """
   This represents a single person taking part in the project.
   
   See base class for attributes
   """
   def __init__(self, ID):
      """
      Parameters
      ----------
      ID : str
      \tUnique identifier for the person
      """
      participant.__init__(self, ID)
      return


class simulated_participant(participant):
   """
   This represents a single person taking part in the project.

   See base class for attributes
   """
   def __init__(self, ID):
      """
      Parameters
      ----------
      ID : str
      \tUnique identifier for the person
      """
      participant.__init__(self, ID)
      self.digicomp_initial = np.nan
      self.digicomp_final = np.nan
      self.digicomp_set = False
      return
      
   def set_digicomp(self, digicomp_initial, digicomp_final):
      self.digicomp_initial = digicomp_initial
      self.digicomp_final = digicomp_final
      self.digicomp_set = True
      return
   
   def calculate_results(self, n_sessions, n_skills):
      """
      Simulate results of a learning module. This requires digital
      competence to already have been set.
      """
      if self.digicomp_set:
         self.n_sessions = n_sessions
         self.n_skills = n_skills
         self.results = np.zeros((n_sessions, n_skills), dtype = bool)
         flat_random = rd.random((n_sessions, n_skills))
         digicomp_array = np.tile(np.linspace(self.digicomp_initial, self.digicomp_final, num = n_sessions), (n_skills, 1)).T
         self.results = flat_random < digicomp_array
         self.results_read = True
         self._evaluate_results_according_to_last_wrong()
      else:
         print('Digicomp needs to be set to calculate results before and after')
      return


class learning_module(ABC):
   """
   This represents one learning module in the project.
  
   The participants are divided into smaller groups, first according to
   the known BBVs and then according to the manipulations.
   """
   def __init__(self, n_skills, n_sessions, boundaries):
      """
      This simply sets some dummy values which must be defined by the
      inheriting classes. It must be passed something to act as a boundaries
      object, although this can simply be a None.
      """
      self.boundaries = boundaries
      
      self.n_participants = np.nan
      self.n_skills = n_skills
      self.n_sessions = n_sessions

      self.n_BBVs = np.nan      
      self.known_BBVs = []
      self.discovered_BBVs = []
      self.unknown_BBVs = []

      self.ids = []
      self.participants = []
      
      self.BBVs = []
      self.BBV_flags = {}
      
      self.n_CBV = np.nan     
      self.CBVs = []
      self.CBV_values = {}
      
      self.n_manipulations = np.nan
      self.manipulations = {}
      self.manipulation_flags = {}
      self.manipulation_groups = {}

      self.all_flags = {}

      self.results = np.asarray([])
      self.results_initial = np.asarray([])
      self.results_final = np.asarray([])
      self.ranking_by_session = np.asarray([])
      self.ranking = np.asarray([])
      return
   
   ### Method for ranking participants based on results
   
   def _rank_participants(self):
      self.ranking_by_session = np.zeros((self.n_sessions, self.n_participants))
      for i in range(self.n_sessions):
         self.ranking_by_session[i,:] = ordinalise(self.results[i,:])
         
      total_ranking = np.zeros(self.n_participants)
      
      for i in range(self.n_sessions - 1):
         # Unless you explicitly make this a float, the type of (self.n_participants + 1)**i
         # suddenly changes once i is big enough. I do not know if this is a bug in numpy or
         # a feature so clever I cannot understand it.
         total_ranking += self.ranking_by_session[-1-i,:] / float((self.n_participants + 1)**i)
      self.ranking = ordinalise(total_ranking)
      return
   
   ### Methods for setting manipulations
   
   def _set_manipulation_flags(self):
      n_manipulations = len(self.manipulations)

      manipulation_flags = {}
      for i in range(n_manipulations):
         flags = np.zeros(self.n_participants, dtype = np.bool)
         manipulation = self.manipulations[i]

         for subgroup_name, subgroup_indices in self.subgroups.items():
            n_blocks = 2**(i+1)
            block_exact_breakpoints = np.linspace(0, len(subgroup_indices), 2**(i+1) + 1)
            block_breakpoints = np.rint(block_exact_breakpoints).astype(int)
         
            for start, stop in zip(block_breakpoints[0:-2:2], block_breakpoints[1:-1:2]):
               flags[subgroup_indices[start:stop]] = True
            manipulation_flags[manipulation.name] = flags
      return manipulation_flags

   def set_manipulations(self, manipulations):
      """
      Takes a list of manipulations and defines flags stating which
      participants should be subject to which manipulation
      """
      self.manipulations = manipulations
      self.n_manipulations = len(self.manipulations)
      self.manipulation_flags = self._set_manipulation_flags()
      self.all_flags = {**self.manipulation_flags, **self.BBV_flags}
      self.manipulation_groups = _define_subgroups(self.n_participants, self.manipulations, self.manipulation_flags)
      return
         
   
   ### Methods for saving data to disk
   
   def save_ids(self, path):
      """
      Save a file listing the participant IDs
      """
      f = open(path, 'w')
      packed = json.dumps({'IDs':self.ids})
      f.write(packed)
      f.close()
      return

   def save_CBVs(self, path):
      """
      Save a file naming the CBVs affecting the participants and listing the
      values of the CBVs for each participant.
      """
      jsonable_CBV_names = {}
      jsonable_CBV_values = {}
      
      for CBV in self.CBVs:
         jsonable_CBV_names.append(CBV.name)
         jsonable_CBV_flags = self.CBV_values[CBV.name].tolist()
      f = open(path, 'w')
      packed = json.dumps({'IDs':self.ids, 'CBVs': jsonable_CBV_names, 'CBV values':jsonable_CBV_values})
      f.write(packed)
      f.close()
      return

   def save_BBVs(self, path):
      """
      Save a file naming the BBVs affecting the participants and listing
      boolean flags describing which participant is affected by which BBV
      """
      jsonable_BBV_names = {}
      jsonable_BBV_flags = {}
      
      for wording, BBV_list in [("discovered", self.discovered_BBVs), ("known", self.known_BBVs)]:
         jsonable_BBV_names[wording] = []
         for BBV in BBV_list:
            jsonable_BBV_names[wording].append(BBV.name)
            jsonable_BBV_flags[BBV.name] = self.BBV_flags[BBV.name].tolist()
      f = open(path, 'w')
      packed = json.dumps({'IDs':self.ids, 'BBVs': jsonable_BBV_names, 'BBV flags':jsonable_BBV_flags})
      f.write(packed)
      f.close()
      return

   def save_manipulations(self, path):
      """
      Save a file starting with the manipulations, followed by suggested
      flags for the participants
      """
      jsonable_manipulation_names = []
      jsonable_manipulation_flags = {}
      for manipulation in self.manipulations:
         jsonable_manipulation_names.append(manipulation.name)
         jsonable_manipulation_flags[manipulation.name] = self.manipulation_flags[manipulation.name].tolist()
      f = open(path, 'w')
      packed = json.dumps({'IDs':self.ids, 'Manipulations': jsonable_manipulation_names, 'Manipulation flags':jsonable_manipulation_flags})
      f.write(packed)
      f.close()
      return

   def save_results(self, folder_path):
      for participant in self.participants:
         participant.save_results(folder_path)
      return


   ### Methods for reading data from disk
   
   def load_ids(self, path):
      """
      Read participant IDs from a file
      """
      f = open(path, 'r')
      packed = f.read()
      f.close()
      unpacked = json.loads(packed)
      self.ids = unpacked['IDs']
      self.n_participants = len(self.ids)
      
      self.participants = []
      for ID in self.ids:
         self.participants.append(real_participant(ID))
      return

   def load_CBVs(self, path):
      """
      Read a file with CBVs and the values for each participant
      """
      f = open(path, 'r')
      packed = f.read()
      f.close()
      unpacked = json.loads(packed)
      
      ids = unpacked['IDs']
      CBVs = []
      for name in unpacked['CBVs']:
         CBVs.append(real_CBV(name))
      CBV_values = unpacked['CBV values']
      
      for CBV in CBVs:
         try:
            CBV_values[CBV.name] = np.asarray(_match_ids(self.ids, ids, CBV_values[CBV.name]), dtype = np.bool)
         except IDMismatchError:
            print("Cannot read data from file!")
            print("IDs in file do not match IDs of participants in study")
            return
      self.CBVs = CBVs
      self.CBV_values = CBV_values
      self.n_CBV = len(CBVs)
      return
      
   def load_BBVs(self, path):
      """
      Read a file with BBVs and the boolean flags describing which
      participants are affected
      """
      f = open(path, 'r')
      packed = f.read()
      f.close()
      unpacked = json.loads(packed)
      
      ids = unpacked['IDs']
      known_BBVs = []
      discovered_BBVs = []
      for name in unpacked['BBVs']['known']:
         known_BBVs.append(real_BBV(name))
      for name in unpacked['BBVs']['discovered']:
         discovered_BBVs.append(real_BBV(name))

      BBV_flags = unpacked['BBV flags']
      
      for BBV in known_BBVs + discovered_BBVs:
         try:
            BBV_flags[BBV.name] = np.asarray(_match_ids(self.ids, ids, BBV_flags[BBV.name]), dtype = np.bool)
         except IDMismatchError:
            print("Cannot read data from file!")
            print("IDs in file do not match IDs of participants in study")
            return

      self.known_BBVs = known_BBVs
      self.discovered_BBVs = discovered_BBVs
      # We assume that this is only done in the absence of unknown BBVs
      self.unknown_BBVs = []
      self.BBVs = self.known_BBVs + self.unknown_BBVs
      self.BBV_flags = BBV_flags
      self.n_BBVs = len(known_BBVs)
      return
      
   def load_manipulations(self, path):
      """
      Load a file with manipulations and flags for the participants
      """
      f = open(path, 'r')
      packed = f.read()
      f.close()
      unpacked = json.loads(packed)
      
      ids = unpacked['IDs']
      manipulations = []
      for name in unpacked['Manipulations']:
         manipulations.append(real_manipulation(name))
      manipulation_flags = unpacked['Manipulation flags']
      
      for manipulation in manipulations:
         try:
            manipulation_flags[manipulation.name] = np.asarray(_match_ids(self.ids, ids, manipulation_flags[manipulation.name]), dtype = np.bool)
         except IDMismatchError:
            print("Cannot read data from file!")
            print("IDs in file do not match IDs of participants in study")
            return

      self.manipulations = manipulations
      self.manipulation_flags = manipulation_flags
      self.n_manipulations = len(manipulations)
      return

   def load_results(self, folder_path):
      self.results = np.zeros((self.n_sessions, self.n_participants))
      for i in range(self.n_participants):
         participant = self.participants[i]
         participant.load_results(folder_path)
         self.results[:,i] = participant.correct_onwards[0:self.n_sessions]# The slicing deals with the unusual case where a module formally contains more than the standard number of sessions for one skill.
      self.results_initial = self.results[0,:]
      self.results_final = self.results[self.n_sessions - 1,:]
      self._rank_participants()
      return


class simulated_learning_module(learning_module):
   """
   See base class learning_module for definition.
   
   This is used when simulating a study. It requires the user to specify:
   
    - Initial distribution over digital competence
   
    - Unknown BBVs, if any, affecting the participants
  
   Attributes
   ----------
   n : int
   \tThe number of participants in the study
   default_digicomp : float
   \tThe digital competence of participants affected by no BBV
   \tvariables, prior to taking the learning module
   known_BBVs : list of simulated_BBV
   \tBBVs that affect some subset of participants, and which are
   \tassumed to be known to the experimenters ahead of time. This means
   \tthat it is possible for them to divide the participants affected
   \tby these BBV variables evenly w.r.t. the manipulations
   discovered_BBVs : list of simulated_BBV
   \tBBVs that affect some subset of participants, and which are
   \tassumed to be discovered by the experimenters in the course of the
   \tlearning module. This means that it is not possible for them to
   \tdivide the participants affected by these BBV variables
   \tevenly w.r.t. the manipulations
   unknown_BBVs : list of simulated_BBV
   \tBBVs that affect some subset of participants, and which are
   \tassumed to be unknown to the experimenters even after the learning
   \tmodule.
   BBVs : list of simulated_BBV
   \tList containing both the known and unknown BBVs
   BBV_flags : dict of bool ndarrays
   \tDictionary containing arrays stating which participants are
   \taffected by which BBVs
   CBVs : list of simulated_CBV
   \tDictionary containing all CBVs
   CBV_values : dict of float ndarrays
   \tDictionary containing arrays stating the values of the CBVs for each
   \tparticipant
   subgroups : dict of int ndarrays
   \tDictionary containing the indices of the participants in each
   \tsubgroup
   digicomp_initial : float ndarray
   \tThe digital competence of the participants before taking the module
   digicomp_final : float ndarray
   \tThe digital competence of the participants after taking the module.
   \tThis is initially set to nan, and can be calculated by supplying some
   \tdefault effect of the module, and optionally a list of manipulations.
   \tTypically, this is done by a study object.
   digicomp_set : bool
   \tWhether anything has set digicomp_initial and digicomp_final
   """
   def __init__(self, n_skills, n_sessions, n_participants, default_digicomp, default_effect, known_BBVs = [], discovered_BBVs = [], unknown_BBVs = [], CBVs = [], boundaries = None):
      """
      Parameters
      ----------
      n : int
      \tDescribed under attributes
      default_digicomp : float
      \tDescribed under attributes
      
      Optional parameters
      -------------------
      known_BBVs : list of BBV
      \tDescribed under attributes
      discovered_BBVs : list of BBV
      \tDescribed under attributes
      unknown_BBVs : list of BBV
      \tDescribed under attributes
      CBVs : list of CBV
      \tDescribed under attributes
      boundaries : boundaries
      \tDescribed under boundaries
      """
      learning_module.__init__(self, n_skills, n_sessions, boundaries)
      self.n_participants = n_participants

      self.ids = [str(number) for number in range(self.n_participants)]
      for ID in self.ids:
         self.participants.append(simulated_participant(ID))

      self.default_digicomp = default_digicomp
      self.default_effect = default_effect
      self.known_BBVs = known_BBVs
      self.discovered_BBVs = discovered_BBVs
      self.unknown_BBVs = unknown_BBVs
      self.BBVs = self.known_BBVs + self.discovered_BBVs + self.unknown_BBVs
      self.n_BBV = len(self.BBVs)
      self.BBV_flags = {}
      for BBV in self.BBVs:
         self.BBV_flags[BBV.name] = rd.random(self.n_participants) < BBV.fraction
      
      self.CBVs = CBVs
      self.CBV_values = {}
      for CBV in self.CBVs:
         self.CBV_values[CBV.name] = CBV.PDF(self.n_participants)
      self.n_CBV = len(self.CBVs)
      
      #Divide the participants into subgroups where the members are subject
      #to the same known BBVs
      self.subgroups = _define_subgroups(self.n_participants, self.known_BBVs, self.BBV_flags)
      self.digicomp_initial = self._calculate_digicomp_initial()

      # This cannot be calculated without a study object that specifies the
      # default effect of the learning modules and any manipulations
      self.digicomp_final = np.nan * np.zeros(self.n_participants)
      return
   
   ### Methods for calculating digital competence
   
   def _calculate_digicomp_initial(self):
      """
      Calculate the digital competence prior to the start of the course,
      using the default and adding the relevant BBV effects
      """
      digicomp_initial = np.ones(self.n_participants) * self.default_digicomp
      for BBV in self.BBVs:
          digicomp_initial[self.BBV_flags[BBV.name]] = BBV.pre_transformation(digicomp_initial[self.BBV_flags[BBV.name]])
      for CBV in self.CBVs:
          digicomp_initial = CBV.pre_transformation(digicomp_initial, self.CBV_values[CBV.name])
      return digicomp_initial
      
   def calculate_digicomp_final(self, manipulations = [], manipulation_flags = []):
      """
      Calculates the digital competence after finishing the course. To do
      this a default effect, together with manipulations and manipulation
      flags must be provided.
      """
      self.digicomp_final = self.default_effect(self.digicomp_initial)
      
      for manipulation in manipulations:
         self.digicomp_final[manipulation_flags[manipulation.name]] = manipulation.transformation(self.digicomp_final[manipulation_flags[manipulation.name]])
      for BBV in self.BBVs:
         self.digicomp_final[self.BBV_flags[BBV.name]] = BBV.post_transformation(self.digicomp_final[self.BBV_flags[BBV.name]])
      for CBV in self.CBVs:
         self.digicomp_final = CBV.post_transformation(self.digicomp_final, self.CBV_values[CBV.name])
      return
      
   ### Methods for calculating results based on digital competence
   
   def calculate_results(self):
      self.results = np.zeros((self.n_sessions, self.n_participants))
      for i in range(self.n_participants):
         participant, digicomp_initial, digicomp_final = self.participants[i], self.digicomp_initial[i], self.digicomp_final[i]
         participant.set_digicomp(digicomp_initial, digicomp_final)
         participant.calculate_results(self.n_sessions, self.n_skills)
         self.results[:,i] = participant.correct_onwards
      self.results_initial = self.results[0,:]
      self.results_final = self.results[self.n_sessions - 1,:]
      self._rank_participants()
      return

   ### Method for running simulation
   
   def run_simulation(self):
      """
      Simulate the participants taking their various versions of the course,
      increasing in digital competence as they do so.
      """
      self.calculate_digicomp_final(self.manipulations, self.manipulation_flags)
      self.calculate_results()
      return

   ### Methods for output
   
   def describe(self):
      """
      Gives a summary of the most important facts about the participants
      """
      print("Description of the participants:\n")
      print("There {} {} participant{}".format(_is_are(self.n_participants), self.n_participants, _plural_ending(self.n_participants)))
      for wording, BBV_list in [("known", self.known_BBVs), ("discovered", self.discovered_BBVs), ("unknown", self.unknown_BBVs)]:
         print("\nThere {} {} BBV{} {} to the experimenters".format(_is_are(self.n_BBV), self.n_BBV, _plural_ending(self.n_BBV), wording))
         for BBV in BBV_list:
            n_affected = np.sum(self.BBV_flags[BBV.name])
            print("{}BBV: {}".format(_indent(1), BBV.name))
            print("{}Affects {} participant{}".format(_indent(2), n_affected, _plural_ending(n_affected)))
            print("{}Which makes up {:.2f} of total".format(_indent(2), n_affected / self.n_participants))
      
      if len(self.known_BBVs) > 0:
         print("\nThe known BBVs require splitting the group into the following subgroups")
         for subgroup_name, subgroup_members in self.subgroups.items():
            n_members = len(subgroup_members)
            print("{}'{}'".format(_indent(1), subgroup_name))
            print("{}Has {} member{}".format(_indent(2), n_members, _plural_ending(n_members)))
            for wording, BBV_list in [("discovered", self.discovered_BBVs), ("unknown", self.unknown_BBVs)]:
               print("{}Out of these, some may be affected by {} BBVs:".format(_indent(2), wording))
               for BBV in BBV_list:
                  print("{}{}: {}".format(_indent(3), BBV.name, sum(self.BBV_flags[BBV.name][subgroup_members])))
      if self.n_CBV > 0:
         print("\nThere {} {} CBV{}".format(_is_are(self.n_CBV), self.n_CBV, _plural_ending(self.n_CBV)))
         for CBV in self.CBVs:
            print("{}CBV: {}".format(_indent(1), CBV.name))
            print("{}Median: {:.2f}".format(_indent(1), np.median(self.CBV_values[CBV.name])))
            print("{}Mean: {:.2f}".format(_indent(1), np.mean(self.CBV_values[CBV.name])))
            print("{}Range: {:.2f}-{:.2f}".format(_indent(1), min(self.CBV_values[CBV.name]), max(self.CBV_values[CBV.name])))
      print("\n")
      return


class real_learning_module(learning_module):
   """
   See base class learning_module for definition.
   
   This needs to read three files of participant IDs, BBVs and
   digital competence.
   
   *Attributes to be added*
   """
   def __init__(self, n_skills, n_sessions, id_path, results_folder_path, manipulation_path = None, CBV_path = None, BBV_path = None, boundaries = None):
      learning_module.__init__(self, n_skills, n_sessions, boundaries)
      self.load_ids(id_path)
      if manipulation_path != None:
         self.load_manipulations(manipulation_path)
      if CBV_path != None:
         self.load_CBVs(CBV_path)
      if BBV_path != None:
         self.load_BBVs(BBV_path)
      self.load_results(results_folder_path)
      #Divide the participants into subgroups where the members are subject
      #to the same known BBVs
      self.subgroups = _define_subgroups(self.n_participants, self.known_BBVs, self.BBV_flags) # Note to self: Is this really correct?!
      return


class study:
   """
   This represents the analysis of the results of a learning module. This
   can be either a simulated learning module or the results of a real one.
   
   Attributes
   ----------
   name : string
   \tName of the study. Used for filenames when plotting.
   learning_module : learning_module
   \tThe learning module that we are studying the results of
   boundaries : boundaries or None
   \tThe boundaries defining what counts as good or poor results
   boundary_tests_run: bool
   \tWhether statistical tests using the boundaries have been run
   measured_results : dict
   \tDictionary containing the results of the statistical analysis
   plot_folder : str
   \tPath to a folder where plots can be saved. If none is specified,
   \tplots will be displayed but not saved.
   """
   def __init__(self, name, learning_module, boundaries = None):
      """
      Parameters
      ----------
      name : string
      \tDescribed under attributes
      learning_module : learning_module
      \tDescribed under attributes
      
      Optional parameters
      -------------------
      boundaries : boundaries
      \tBoundaries defining good and poor test results
      """
      self.name = name
      self.learning_module = learning_module
      
      self.boundaries = boundaries
      self.boundary_tests_run = False

      
      # The results of a statistical analysis of the participants' digital
      # competence before and after taking the course module
      self.measured_results = {}
      
      self.plot_folder = None
      
      # Used when calculating and comparing the qualities for different
      # versions of the course
      self._qk_samples = self.learning_module.n_participants * 10
      self._qk_sample_width = 1 / self._qk_samples
      self._Qki_range = np.linspace(0.0, 1.0, num=self._qk_samples)
      self._dk_samples = 2 * self._qk_samples - 1
      self._Dk_range = np.linspace(-1.0, 1.0, num=self._dk_samples)
      return
      

   ### Functions using standard frequentist tests

   def _compare_flagged(self, flags, results):
      treatment_group = results[flags]
      control_group = results[np.invert(flags)]
      
      statistics = {}
      statistics['treatment group median'] = np.median(treatment_group)
      statistics['control group median'] = np.median(control_group)
      if len(treatment_group) > 0 and len(control_group) > 0:
         s, p, m, table = st.median_test(treatment_group, control_group, ties = "above")
         statistics['median test test statistic'] = s
         statistics['median test p-value'] = p
         statistic, pvalue = st.mannwhitneyu(treatment_group, control_group)
         statistics['Mann-Whitney U rank test test statistic'] = statistic
         statistics['Mann-Whitney U rank test p-value'] = pvalue
      else:
         statistics['median test test statistic'] = np.nan
         statistics['median test p-value'] = np.nan
         statistics['Mann-Whitney U rank test test statistic'] = np.nan
         statistics['Mann-Whitney U rank test p-value'] = np.nan
      return statistics

      
   ### Functions shared between boundary and median tests
   
   def _make_percentiles(self, variable_range, distribution):
      percentiles = [0.13, 2.28, 15.87, 25.0, 50.0, 75.0, 84.13, 97.72, 99.87]
      n_percentiles = len(percentiles)
      percentile_indices = range(n_percentiles)
      percentile_passed = np.zeros(n_percentiles, np.bool)
      
      CDF = 0
      percentile_dict = {}
      for i in range(len(distribution)):
         CDF += distribution[i]
         for j in percentile_indices:
            if not percentile_passed[j]:
               percentile = percentiles[j]
               fraction = percentile / 100
               if CDF > fraction:
                  percentile_passed[j] = True
                  percentile_dict[percentile] = variable_range[i]
      return percentile_dict
   
   def _calculate_qki_and_fill_in_dict(self, log_qki, dictionary):
      qki = np.exp(log_qki)
      nan_qki = np.sum(np.isnan(qki))
      if nan_qki != 0:
         print("Problem in calculation!")
         print("Out of {} calculated values of qki {} {} nan".format(self._qk_samples, nan_qki, _is_are(nan_qki)))
         print("Skipping boundary tests")
         return

      qki_mass = qki * self._qk_sample_width
      total_mass = sum(qki_mass)
      if np.abs(total_mass - 1) > 0.01:
         print("Problem in calculation!")
         print("probability density function not well normalised")
         print("Total probability mass {:.2f}".format(total_mass))
      dictionary['probabilities of qualities'] = qki
      dictionary['log-probabilities of qualities'] = log_qki
      dictionary['probability mass per sampled quality'] = qki_mass
      dictionary['peak of Qki'] = self._Qki_range[np.argmax(qki)]
      dictionary['percentiles of qki'] = self._make_percentiles(self._Qki_range, qki_mass)
      dictionary['median of qki'] = dictionary['percentiles of qki'][50.0]
      return
      
   def _fill_dictionary_with_qk_and_dk(self, dictionary, practical_significance_cutoff):
      qktreat = dictionary['treatment group']['probability mass per sampled quality']
      qkcont = dictionary['control group']['probability mass per sampled quality']
      dk = np.convolve(qktreat, np.flip(qkcont))
      
      dictionary['range of quality differences'] = self._Dk_range
      dictionary['probabilities of quality differences'] = dk
      dictionary['peak of dk'] = self._Dk_range[np.argmax(dk)]
      dictionary['percentiles of dk'] = self._make_percentiles(self._Dk_range, dk)
      dictionary['median of dk'] = dictionary['percentiles of dk'][50.0]
      PDl0 = np.sum(dk[:self._qk_samples])
      PDg0 = np.sum(dk[self._qk_samples+1:])
      dictionary['probability that treatment group does better than control group'] = PDg0
      dictionary['probability that treatment group does worse than control group'] = PDl0

      # Look very closely at this
      cutoff = int(practical_significance_cutoff / self._qk_sample_width)

      PDll0 = np.sum(dk[:self._qk_samples - cutoff])
      PDap0 = np.sum(dk[self._qk_samples - cutoff:self._qk_samples + cutoff])
      PDgg0 = np.sum(dk[self._qk_samples + cutoff:])
      dictionary['probability that treatment group does much better than control group'] = PDgg0
      dictionary['probability that treatment group does much worse than control group'] = PDll0
      dictionary['probability that treatment group does about as well as control group'] = PDap0
      return dictionary
   
   ### Functions specific to the boundary tests

   def _logL_bounds(self, Qki, nl, nlh):
      """
      The log-probability over the quality, where quality is defined as the
      probability that a person who initially had low digital competence will
      have high digital competence after the course module. This requires
      definition of bounds for low and high quality when creating the study.
      """
      with np.errstate(all = 'ignore'):
         log_qki = np.zeros(len(Qki))
         log_qki[1:-1] = nlh * np.log(Qki[1:-1]) + (nl - nlh) * np.log(1 - Qki[1:-1]) - logB(nlh + 1, nl - nlh + 1)
         if nlh > 0:
            log_qki[0] = - np.inf
         else:
            log_qki[0] = - logB(nlh + 1, nl - nlh + 1)
         if nl - nlh > 0:
            log_qki[-1] = - np.inf
         else:
            log_qki[-1] = - logB(nlh + 1, nl - nlh + 1)
      return log_qki
      
   def _boundary_tests(self, pre, post):
      poor = self.learning_module.boundaries.poor
      good = self.learning_module.boundaries.good
      
      boundary_test_result = {}
      boundary_test_result['members with initially poor skills'] = np.count_nonzero(pre < poor)
      boundary_test_result['members with initially good skills'] = np.count_nonzero(pre > good)
      boundary_test_result['members with finally poor skills'] = np.count_nonzero(post < poor)
      boundary_test_result['members with finally good skills'] = np.count_nonzero(post > good)

      boundary_test_result['members moving from poor to good skills'] = np.count_nonzero(np.logical_and(pre < poor, post > good))
      boundary_test_result['fraction with poor skills acquiring good skills'] = boundary_test_result['members moving from poor to good skills'] / boundary_test_result['members with initially poor skills']
      
      nl = boundary_test_result['members with initially poor skills']
      if nl == 0:
         print("There are no members with initially poor skills!")
      nlh = boundary_test_result['members moving from poor to good skills']
      if nlh == 0:
         print("There are no members who have moved from poor to good skills!")
      self._calculate_qki_and_fill_in_dict(self._logL_bounds(self._Qki_range, nl, nlh), boundary_test_result)
      return boundary_test_result
      
   def _boundary_test_total(self, learning_module):
      """
      Runs boundary tests for the entire module, to check whether it has any
      noteworthy effect to begin with.
      """
      return self._boundary_tests(learning_module.results_initial, learning_module.results_final)

   def _boundary_test_BBV_or_manipulation(self, flags, learning_module):
      """
      Runs boundary tests with respect to some BBV or manipulation.
      """
      treatment_group_initial = learning_module.results_initial[flags]
      control_group_initial = learning_module.results_initial[np.invert(flags)]
      treatment_group_final = learning_module.results_final[flags]
      control_group_final = learning_module.results_final[np.invert(flags)]
      
      poor = self.learning_module.boundaries.poor
      good = self.learning_module.boundaries.poor
      
      boundary_tests = {'treatment group':{}, 'control group':{}}
      for text, pre, post in [('treatment group', treatment_group_initial, treatment_group_final), ('control group', control_group_initial, control_group_final)]:
         boundary_tests[text] = self._boundary_tests(pre, post)
      
      self._fill_dictionary_with_qk_and_dk(boundary_tests, self.learning_module.boundaries.minimum_quality_difference)
      self.boundary_tests_run = True
      return boundary_tests
      
   ### Functions specific to the Bayesian median tests
      
   def _logL_median(self, Qki, nki, n_good):
      with np.errstate(all = 'ignore'):
         log_qki = np.zeros(len(Qki))
         log_qki[1:-1] = n_good * np.log(Qki[1:-1]) + (nki - n_good) * np.log(1 - Qki[1:-1]) - logB(n_good + 1, nki - n_good + 1)
         if n_good > 0:
            log_qki[0] = - np.inf
         else:
            log_qki[0] = - logB(n_good + 1, nki - n_good + 1)
         if nki - n_good > 0:
            log_qki[-1] = - np.inf
         else:
            log_qki[-1] = - logB(n_good + 1, nki - n_good + 1)
      return log_qki
      
   def _median_tests(self, control, treat):
      median = np.median(np.concatenate([control, treat]))
      
      median_test_result = {'control group':{}, 'treatment group':{}}
      median_test_result['control group']['total members'] = len(control)
      median_test_result['control group']['members below median'] = np.count_nonzero(control < median)
      median_test_result['control group']['members above median'] = np.count_nonzero(control > median)
      median_test_result['control group']['members on median'] = np.count_nonzero(control == median)
      median_test_result['treatment group']['total members'] = len(treat)
      median_test_result['treatment group']['members below median'] = np.count_nonzero(treat < median)
      median_test_result['treatment group']['members above median'] = np.count_nonzero(treat > median)
      median_test_result['treatment group']['members on median'] = np.count_nonzero(treat == median)

      for group, group_name in [(control, 'control group'), (treat, 'treatment group')]:
         n_good = median_test_result[group_name]['members above median']
         n_ki = median_test_result[group_name]['total members']
         log_qki = self._logL_median(self._Qki_range, n_ki, n_good)
         self._calculate_qki_and_fill_in_dict(log_qki, median_test_result[group_name])
      return median_test_result
      
   def _median_test_total(self, learning_module):
      """
      Runs median tests for the entire module. This tests whether the skills
      before or after taking the module are higher than the median skill for
      both before and after taking the module.
      
      Note that this compares participants against a group that includes
      themselves at another point in time.
      """
      median_tests = {}
      median_tests['after module'] = self._median_tests(learning_module.results_initial, learning_module.results_final)
      median_tests['before module'] = self._median_tests(learning_module.results_final, learning_module.results_initial)
      self._fill_dictionary_with_qk_and_dk(median_tests['after module'], 0.1) 
      return median_tests
      
   def _median_test_BBV_or_manipulation(self, flags, learning_module):
      """
      This tests how likely it seems to be that a participant in either the
      control or treatment group does better than the median for the control
      and treatment groups together.
      
      Note that when looking at the results after the module, it uses the
      ranking, which makes use of all results.
      """
      treatment_group_initial = learning_module.results_initial[flags]
      control_group_initial = learning_module.results_initial[np.invert(flags)]
      
      treatment_group_ranks = learning_module.ranking[flags]
      control_group_ranks = learning_module.ranking[np.invert(flags)]
      
      median_tests = {}
      for text, control, treat in [('before module', control_group_initial, treatment_group_initial), ('after module', control_group_ranks, treatment_group_ranks)]:
         median_tests[text] = self._median_tests(control, treat)
         self._fill_dictionary_with_qk_and_dk(median_tests[text], 0.1) # Fix magic number
      return median_tests
   
   ### Functions that run the tests above
   
   def do_tests(self):
      """
      Runs the statistical analysis on the participants' results
      """
      self.measured_results = {}
      self.measured_results['quick tests'] = {}
      for manipulation in self.learning_module.manipulations:
         self.measured_results['quick tests'][manipulation.name] = self._compare_flagged(self.learning_module.manipulation_flags[manipulation.name], self.learning_module.results_final)
      for BBV in self.learning_module.known_BBVs + self.learning_module.discovered_BBVs:
         self.measured_results['quick tests'][BBV.name] = self._compare_flagged(self.learning_module.BBV_flags[BBV.name], self.learning_module.results_final)
         
      self.measured_results['quick tests']['total'] = {}
      self.measured_results['quick tests']['total']['pre-course median'] = np.median(self.learning_module.results_initial)
      self.measured_results['quick tests']['total']['post-course median'] = np.median(self.learning_module.results_final)
      n_improved = np.sum(self.learning_module.results_final > self.learning_module.results_initial)
      with np.errstate(divide = 'ignore'):
         pvalue = st.binom_test(n_improved, self.learning_module.n_participants)
      self.measured_results['quick tests']['total']['sign test p-value'] = pvalue

      self.measured_results['median tests'] = {}
      self.measured_results['median tests']['total'] = self._median_test_total(self.learning_module)
      for manipulation in self.learning_module.manipulations:     
         self.measured_results['median tests'][manipulation.name] = self._median_test_BBV_or_manipulation(self.learning_module.manipulation_flags[manipulation.name], self.learning_module)
      for BBV in self.learning_module.known_BBVs + self.learning_module.discovered_BBVs:
         self.measured_results['median tests'][BBV.name] = self._median_test_BBV_or_manipulation(self.learning_module.BBV_flags[BBV.name], self.learning_module)
         
      if self.learning_module.boundaries != None:
         self.measured_results['boundary tests'] = {}
         self.measured_results['boundary tests']['total'] = self._boundary_test_total(self.learning_module)
         for manipulation in self.learning_module.manipulations:
            self.measured_results['boundary tests'][manipulation.name] = self._boundary_test_BBV_or_manipulation(self.learning_module.manipulation_flags[manipulation.name], self.learning_module)
         for BBV in self.learning_module.known_BBVs + self.learning_module.discovered_BBVs:
            self.measured_results['boundary tests'][BBV.name] = self._boundary_test_BBV_or_manipulation(self.learning_module.BBV_flags[BBV.name], self.learning_module)
      return

   ### Functions for giving print output
   
   def describe(self):
      """
      Gives a summary of the most important facts about the study, which
      are assumed to be known prior to the study being carried out.
      """
      print("Description of the study itself:\n")
      print("There {} {} participant{}".format(_is_are(self.learning_module.n_participants), self.learning_module.n_participants, _plural_ending(self.learning_module.n_participants)))
      print("We are testing {} manipulation{}:".format(self.learning_module.n_manipulations, _plural_ending(self.learning_module.n_manipulations)))
      for manipulation in self.learning_module.manipulations:
         print("{}{}".format(_indent(1), manipulation.name))
      print("")
         
      n_BBVs = len(self.learning_module.known_BBVs)
      if n_BBVs > 0:
         print("There {} {} known BBV{}:".format(_is_are(n_BBVs), n_BBVs, _plural_ending(n_BBVs)))
         for BBV in self.learning_module.known_BBVs:
            print("{}{}".format(_indent(1), BBV.name))
         print("Hence, the participants are split into {} subgroups\n".format(len(self.learning_module.subgroups)))

      n_discovered_BBVs = len(self.learning_module.discovered_BBVs)
      if n_discovered_BBVs > 0:
         print("There {} {} discovered BBV{}:".format(_is_are(n_discovered_BBVs), n_discovered_BBVs, _plural_ending(n_discovered_BBVs)))
         for BBV in self.learning_module.discovered_BBVs:
            print("{}{}\n".format(_indent(1), BBV.name))
         
      n_unknown_BBVs = len(self.learning_module.unknown_BBVs)
      if n_unknown_BBVs > 0:
         print("There {} {} unknown BBV{}:".format(_is_are(n_unknown_BBVs), n_unknown_BBVs, _plural_ending(n_unknown_BBVs)))
         for BBV in self.learning_module.unknown_BBVs:
            print("{}{}".format(_indent(1), BBV.name))
         print("This may affect the study\n")
         
      if self.learning_module.n_CBV > 0:
         print("There {} {} CBV{}:".format(_is_are(self.learning_module.n_CBV), self.learning_module.n_CBV, _plural_ending(self.learning_module.n_CBV)))
         for CBV in self.learning_module.CBVs:
            print("{}{}".format(_indent(1), CBV.name))
         print("")
         
      print("Group membership:")
      for subgroup_name, subgroup_members in self.learning_module.subgroups.items():
         n_members = len(subgroup_members)
         print("{}Group '{}' has {} member{}".format(_indent(1), subgroup_name, n_members, _plural_ending(n_members)))
         # Maybe move this?
         subgroup_members = set(subgroup_members)
         for manipulation_group_name, manipulation_group_members in self.learning_module.manipulation_groups.items():
            manipulation_members = set(manipulation_group_members)
            subgroup_manipulation = subgroup_members.intersection(manipulation_members)
            print("{}Manipulation group '{}' has {} members".format(_indent(2), manipulation_group_name, len(subgroup_manipulation)))
      print("\n")
      return
      
   def summarise_results(self):
      """
      Summarise the findings that the experimentalists have at the end of the
      study
      """
      def print_poor_to_high(group_name, group_data, base_indent):
         print("{}In {}, out of {} members with poor skills {} acquire good skills".format(_indent(base_indent), group_name, group_data['members with initially poor skills'], group_data['members moving from poor to good skills']))
         print("{}Quality estimated to be: {:.2f}".format(_indent(base_indent + 1), group_data['median of qki']))
         print("{}One sigma bounds at: {:.2f} - {:.2f}".format(_indent(base_indent + 1), group_data['percentiles of qki'][15.87], group_data['percentiles of qki'][84.13]))
         print("{}Two sigma bounds at: {:.2f} - {:.2f}".format(_indent(base_indent + 1), group_data['percentiles of qki'][2.28], group_data['percentiles of qki'][97.72]))
         return
         
      def print_above_median(group_name, group_data, base_indent):
         print("{}In {}, out of {} members {} end up above median".format(_indent(base_indent), group_name, group_data['total members'], group_data['members above median']))
         print("{}Quality estimated to be: {:.2f}".format(_indent(base_indent + 1), group_data['median of qki']))
         print("{}One sigma bounds at: {:.2f} - {:.2f}".format(_indent(base_indent + 1), group_data['percentiles of qki'][15.87], group_data['percentiles of qki'][84.13]))
         print("{}Two sigma bounds at: {:.2f} - {:.2f}".format(_indent(base_indent + 1), group_data['percentiles of qki'][2.28], group_data['percentiles of qki'][97.72]))
         return
      
      def print_dk_permutations(dk_dict, base_indent):
         for descriptor in ['probability that treatment group does better than control group', 'probability that treatment group does worse than control group','probability that treatment group does much better than control group','probability that treatment group does much worse than control group','probability that treatment group does about as well as control group']:
            print("{}{}: {:.2f}".format(_indent(base_indent), descriptor, dk_dict[descriptor]))
         return
      
      def print_total_median(dk_dict, base_indent):
         print("{}After taking the course module, {} out of {} members are above the total median".format(_indent(base_indent), dk_dict['treatment group']['members above median'], dk_dict['treatment group']['total members']))
         print("{}'Quality difference' before and after module estimated to be: {:.2f}".format(_indent(base_indent), dk_dict['median of dk']))
         print("{}One sigma bounds at: {:.2f} - {:.2f}".format(_indent(base_indent), dk_dict['percentiles of dk'][15.87], dk_dict['percentiles of dk'][84.13]))
         print("{}Two sigma bounds at: {:.2f} - {:.2f}".format(_indent(base_indent), dk_dict['percentiles of dk'][2.28], dk_dict['percentiles of dk'][97.72]))
         print_dk_permutations(dk_dict, base_indent)
         return
      
      def print_quality_difference(dk_dict, base_indent):
         print("{}Comparing control group and test group".format(_indent(base_indent)))
         print("{}Quality difference estimated to be: {:.2f}".format(_indent(base_indent + 1), dk_dict['median of dk']))
         print("{}One sigma bounds at: {:.2f} - {:.2f}".format(_indent(base_indent + 1), dk_dict['percentiles of dk'][15.87], dk_dict['percentiles of dk'][84.13]))
         print("{}Two sigma bounds at: {:.2f} - {:.2f}".format(_indent(base_indent + 1), dk_dict['percentiles of dk'][2.28], dk_dict['percentiles of dk'][97.72]))
         print_dk_permutations(dk_dict, base_indent + 1)
         return
         
      tot = self.measured_results['quick tests']['total']
      print("Description of results of study:\n")
      print("Results for course module as a whole:")
      print("{}Results of standard frequentist tests:".format(_indent(1)))
      print("{}p-value of sign test: {:.2}".format(_indent(2), tot['sign test p-value']))
      print("{}Results of bayesian median tests:".format(_indent(1)))
      print_total_median(self.measured_results['median tests']['total']['after module'], 2)
      if self.boundary_tests_run:
         print("{}Results of boundary tests:".format(_indent(1)))
         print_poor_to_high('total', self.measured_results['boundary tests']['total'], 1)
      
      for variation, description in [(self.learning_module.manipulations, 'manipulation'), (self.learning_module.known_BBVs + self.learning_module.discovered_BBVs, 'BBV')]:
         for choice in variation:
            results = self.measured_results['quick tests'][choice.name]
            print("\nResults for {} {}:".format(description, choice.name))
            print("{}Results of standard frequentist tests:".format(_indent(1)))
            print("{}p-value of median test: {:.2}".format(_indent(2),results['median test p-value']))
            print("{}p-value of Mann-Whitney U rank test: {:.2}".format(_indent(2),results['Mann-Whitney U rank test p-value']))
            print("{}Results of bayesian median tests:".format(_indent(1)))
            for group in ['control group', 'treatment group']: 
               print_above_median(group, self.measured_results['median tests'][choice.name]['after module'][group], 2)            
            print_quality_difference(self.measured_results['median tests'][choice.name]['after module'], 2)         
            if self.boundary_tests_run:
               print("{}Results of boundary tests:".format(_indent(1)))
               bound =  self.measured_results['boundary tests'][choice.name]
               for group in ['control group', 'treatment group']:
                  print_poor_to_high(group, bound[group], 2)
               print_quality_difference(bound, 2)
      return
  
   ### Functions for plotting

   def plot_participants(self):
      """
      Plot group membership of all participants
      """
      def plot_flags(flags, name):
         side = int(np.ceil(np.sqrt(self.learning_module.n_participants)))
         i = np.arange(self.learning_module.n_participants)
         x = i % side
         y = i // side
         plt.clf()
         plt.tight_layout()
         plt.scatter(x, y, c = flags, s=1, marker = 's')
         plt.xlim(-1, side+0.5)
         plt.ylim(-1, side-0.5)
         plt.savefig('./{}/ill_{}_groups_{}.png'.format(self.plot_folder, self.name, name))
         return
         
      def plot_group_subgroup(flags_1, flags_2, name_1, name_2):
         # The dummy is to prevent sorted from also sorting based on flags_2
         sorted_1, dummy, sorted_2 = zip(*sorted(zip(flags_1, range(self.learning_module.n_participants), flags_2)))
         side = int(np.ceil(np.sqrt(self.learning_module.n_participants)))
         i = np.arange(self.learning_module.n_participants)
         x = i % side
         y = i // side
         
         plt.clf()
         plt.tight_layout()
         plt.scatter(x, y, c = sorted_2, s=1, marker = 's')
         
         first_true = sorted_1.index(True)
         plt.plot([-1, x[first_true] - 0.5], [y[first_true] + 0.5, y[first_true] + 0.5] , c = 'k', lw = 0.5)
         plt.plot([x[first_true] - 0.5, x[first_true] - 0.5], [y[first_true] - 0.5, y[first_true] + 0.5] , c = 'k', lw = 0.5)
         plt.plot([x[first_true] - 0.5, side], [y[first_true] - 0.5, y[first_true] - 0.5] , c = 'k', lw = 0.5)

         plt.xlim(-1, side)
         plt.ylim(-1, side-0.5)
         plt.savefig('./{}/ill_{}_subgroups_{}_{}.png'.format(self.plot_folder, self.name.replace(' ', '_'), name_1.replace(' ', '_'), name_2.replace(' ', '_')), dpi=400)
         return
      
      for name_1, flags_1 in self.learning_module.all_flags.items():
         plot_flags(flags_1, name_1)
         for name_2, flags_2 in self.learning_module.all_flags.items():
            plot_group_subgroup(flags_1, flags_2, name_1, name_2)
      return

   def plot_results(self):
      """
      Plot the results of the study. This includes:
      
      - The estimated quality of the learning module with and without each
      manipulation
      
      - The logarithm of the above. This can be interesting since the
      distributions often drop off exponentially, meaning that normally only
      a sharp peak is visible.
      
      - The estimated difference between the versions of the learning module
      with and without each manipulation
      """
      def plot_quality(test_name, test_data):
         plt.clf()
         plt.tight_layout()
         plt.plot(self._Qki_range, test_data['control group']['probabilities of qualities'], label = 'Control')
         plt.plot(self._Qki_range, test_data['treatment group']['probabilities of qualities'], label = 'Treatment')
         plt.xlim(0, 1)
         plt.legend()
         plt.savefig('./{}/ill_{}_{}_{}_{}.png'.format(self.plot_folder, self.name.replace(' ', '_'), test_name, description, choice.name.replace(' ', '_')))
               
         plt.clf()
         plt.tight_layout()  
         plt.plot(self._Qki_range, test_data['control group']['log-probabilities of qualities'], label = 'Control')
         plt.plot(self._Qki_range, test_data['treatment group']['log-probabilities of qualities'], label = 'Treatment')
         plt.xlim(0, 1)
         plt.legend()
         plt.savefig('./{}/ill_{}_{}_{}_{}_log.png'.format(self.plot_folder, self.name.replace(' ', '_'), test_name, description, choice.name.replace(' ', '_')))
               
         plt.clf()
         plt.tight_layout()  
         plt.plot(self._Dk_range, test_data['probabilities of quality differences'], label = 'Difference')
         plt.xlim(-1, 1)
         plt.axvline(x = 0.0, c = 'k')
         plt.axvline(x = self.learning_module.boundaries.minimum_quality_difference, linestyle = '--', c = 'k')
         plt.axvline(x =-self.learning_module.boundaries.minimum_quality_difference, linestyle = '--', c = 'k')
         plt.savefig('./{}/ill_{}_{}_{}_{}_difference.png'.format(self.plot_folder, self.name.replace(' ', '_'), test_name, description, choice.name.replace(' ', '_')))
         return
      
      if self.plot_folder == None:
         print("You need to specify a relative path to a folder for the plots")
         return
   
      if not os.path.isdir('./{}'.format(self.plot_folder)):
         print("This needs to be run in the same directory as a directory named '{}'".format(self.plot_folder))
         return

      for variation, description in [(self.learning_module.manipulations, 'manipulation'), (self.learning_module.known_BBVs + self.learning_module.discovered_BBVs, 'BBV')]:
         for choice in variation:
            plot_quality('mtest', self.measured_results['median tests'][choice.name]['after module'])

            if self.boundary_tests_run:
               plot_quality('btest', self.measured_results['boundary tests'][choice.name])
      return
      
class minimal_size_experiment:
   """
   This is intended to run multiple simulations of studies that are
   identical except that the number of participants varies
   """
   def __init__(self, name, default_digicomp, default_effect, n_skills, n_sessions, manipulations, known_BBVs, n_min, n_max, n_steps = 10, iterations = 10):
      """
      Parameters
      ----------
      Under construction
      """
      self.name = name
      self.name_for_file = _trim_for_filename(self.name)
      self.default_digicomp = default_digicomp
      self.default_effect = default_effect
      self.n_skills = n_skills
      self.n_sessions = n_sessions
      self.manipulations = manipulations
      self.known_BBVs = known_BBVs
      self.n_min = n_min
      self.n_max = n_max
      self.n_steps = n_steps
      self.iterations = iterations
      self.ns = np.linspace(self.n_min, self.n_max, num = self.n_steps, endpoint = True, dtype = np.int64)
      self.median_pDpos = {'total':[]}
      for manipulation_or_BBV in self.manipulations + self.known_BBVs:
         self.median_pDpos[manipulation_or_BBV.name] = []     
      self.plot_folder = ''
      return
      
   def run(self):
      for n_participants in self.ns:
         pDpos = {}
         for key in self.median_pDpos.keys():
            pDpos[key] = []
         for i in range(self.iterations):
            part = simulated_learning_module(self.n_skills, self.n_sessions, n_participants, self.default_digicomp, self.default_effect, known_BBVs = self.known_BBVs)
            part.set_manipulations(self.manipulations)            
            part.run_simulation()
            simulated_study = study('Group size {}, simulation {}'.format(n_participants, i), part)
            simulated_study.do_tests()
            pDpos['total'].append(simulated_study.measured_results['median tests']['total']['after module']['probability that treatment group does better than control group'])
            for key in pDpos.keys():
               pDpos[key].append(simulated_study.measured_results['median tests'][key]['after module']['probability that treatment group does better than control group'])
        
         for key in self.median_pDpos.keys():
            self.median_pDpos[key].append(np.median(pDpos[key]))
      return
      
   def plot(self):
      plt.clf()
      for key in self.median_pDpos.keys():
         plt.plot(self.ns, self.median_pDpos[key], label = key)
      plt.xlabel(r"$n$")
      plt.ylabel(r"$P\left( D > 0 \right)$")
      plt.xlim(self.n_min, self.n_max)
      plt.ylim(0, 1)
      plt.legend()
      if self.plot_folder == '':
         plt.show()
      else:
         plt.savefig('./{}/ill_{}_pDpos.png'.format(self.plot_folder, self.name_for_file))
      return
