"""
This module was written for the ESF-financed project Demokratisk
Digitalisering. The project is a collaboration between
Arbetsförmedlingen (AF) and Kungliga Tekniska Högskolan (KTH). The
purpose of the project is to increase the digital competence - as
defined at https://ec.europa.eu/jrc/en/digcomp - of people working at
Arbetsförmedlingen, and by extension also job seekers. This shall be
done by learning modules at KTH using OLI-Torus.

The module is primarily intended as a proof-of-concept. That is, the
main purpose is to simulate data, and then perform the analyses that we
would do on real-world data on that simulated data. However, it should
also be able to take real-world data, once such is available.

One of the assumptions in this model is that digital competence can in
principle be represented as a real number, but that the experimenters
do not have access to that number. That is, behind the scenes we model
digital competence on an interval scale, but the simulated experiment-
ers have to analyse it using an ordinal scale.

The study is assumed to use a factorial design, so that the experiment-
ers first identify some background variables - here referred to as 
'backgrounds '- that are likely to affect the results - such as age or
motivation - and split the participants into several smaller groups
within which all members are affected the same. They then try out a
certain number of changes in the course - here referred to as
'manipulations'. To evaluate the effect of the manipulations the
participant groups are further halved ortogonally, so that with n
manipulations there are 2^n groups that each get some combination of
manipulations.

Written by Alvin Gavel,

alvin.gavel@gmail.com
"""

import numpy as np
import numpy.random as rd
import scipy.special as sp
import scipy.stats as st
import os
import matplotlib.pyplot as plt
import numbers as nb

### Useful tools

def read_nested_dict(dictionary):
   """
   In this module a lot of data is stored as nested dicts. This tool is
   intended to make it easier to inspect them.
   
   Given a dict, you will be shown the keys and some information about
   the corresponding values. For most data types only the type itself is
   printed out. Numeric values are printed out. Strings are printed out
   but shortened if too long. For lists, tuples and sets the length is
   shown.
   
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

def _shop_docstring(docstring):
   """
   Takes a string of documentation and inserts line breaks ensuring each
   line is max 72 characters wide.
   """
   line_maxlen = 72
   full_string = ""
   row = ""
   word = ""
   for character in docstring:
      if character == " ":
         if len(row) + len(word) + 1 >= line_maxlen:
            full_string += row + "\n"
            row = word
         else:
            row += " " + word
         word = ""
      else:
         word += character
   full_string += row + " " + word
   return full_string[1:]

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

### Misc. mathematical stuff

def _ordinalise(ndarray):
   """
   Takes an ndarray and makes the data ordinal. That is to say, the
   elements will be turned into integers denoting the lowest, second
   lowest etcetera.
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
   
def _ordinalise_many(ndarrays):
   """
   Takes a list of ndarrays and puts them on a common ordinal scale.
   """
   concatenated = np.concatenate(ndarrays)
   ordinal_long = _ordinalise(concatenated)
   ordinal = []
   cut = 0
   for ndarray in ndarrays:
      length = len(ndarray)
      ordinal.append(ordinal_long[cut:cut+length])
      cut += length
   return ordinal
   
def logB(alpha, beta):
   """
   The logarithm of the normalisation factor when doing Bayesian fitting
   of binomial functions.
   """
   return sp.loggamma(alpha) + sp.loggamma(beta) - sp.loggamma(alpha + beta)


### Statistical distributions

# These are example statistical distributions that can be used when
# modelling digital competence. They assume that digital competence is
# normally found on a scale from 0 to 100, with some people being above
# that and none being below.

def _normal_dist(n):
   """
   Returns n samples from a normal distribution with mean 25 and standard
   deviation 10
   """
   return rd.normal(loc=25., scale=10, size=n)
   
standard_distributions = {"normal": _normal_dist}

def additive_scatter(digicomp_pre):
   """
   This represents something that affects digital competence by a normal
   variable centered around 0, with std 5. This could be a representation
   of measurement error.
   """
   digicomp_post = digicomp_pre + rd.normal(loc=0, scale=5, size=len(digicomp_pre))
   return digicomp_post

def additive_normal_improvement(digicomp_pre):
   """
   This represents a manipulation or background that increases digital
   competence by a normal variable centered around 10, with std 5.
   """
   digicomp_post = digicomp_pre + rd.normal(loc=10, scale=5, size=len(digicomp_pre))
   return digicomp_post

def additive_normal_improvement_big(digicomp_pre):
   """
   This represents a manipulation or background that increases digital
   competence by a normal variable centered around 20, with std 5.
   """
   digicomp_post = digicomp_pre + rd.normal(loc=20, scale=5, size=len(digicomp_pre))
   return digicomp_post

def subtractive_normal_deterioration(digicomp_pre):
   """
   This represents a manipulation or background that decreases digital
   competence by a normal variable centered around 10, with std 5.
   """
   digicomp_post = digicomp_pre - rd.normal(loc=10, scale=5, size=len(digicomp_pre))
   return digicomp_post

def additive_deterministic_improvement_big(digicomp_pre):
   """
   This represents a manipulation or background that always
   increases digital competence by exactly 20.
   """
   digicomp_post = digicomp_pre + 20
   return digicomp_post

def additive_deterministic_improvement(digicomp_pre):
   """
   This represents a manipulation or background that always
   increases digital competence by exactly 10.
   """
   digicomp_post = digicomp_pre + 10
   return digicomp_post

def subtractive_deterministic_deterioration(digicomp_pre):
   """
   This represents a manipulation or background that always
   increases digital competence by exactly 10.
   """
   digicomp_post = digicomp_pre - 10
   return digicomp_post

def zero_improvement(digicomp_pre):
   """
   This represents a manipulation or background that does nothing to
   digital competence.
   """
   return digicomp_pre[:]

standard_transformations = {"additive scatter":additive_scatter,
                            "additive normal improvement": additive_normal_improvement,
                            "additive normal improvement (big)": additive_normal_improvement_big,
                            "subtractive normal deterioration": subtractive_normal_deterioration,
                            "additive deterministic improvement": additive_deterministic_improvement,
                            "additive deterministic improvement (big)": additive_deterministic_improvement_big,
                            "subtractive deterministic deterioration": subtractive_deterministic_deterioration,
                            "no effect": zero_improvement}

### Classes

class manipulation:
   """
   This represents some change we make to the course, which we try out on
   a subset of the participants. This means that the participants will be
   divided into a control group and a test group, which will be as close
   to a 50/50 split as possible. Where there are known backgrounds, the
   subsets sharing the same backgrounds will also be split approximately
   in half.
   
   As a rule all manipulations are binary. That is, they are either done
   or not done, but there are no manipulations that we try out to varying
   degrees.

   Attributes
   ----------
   name : str
   \tDescription of the manipulation
   name_for_file : str
   \tRendition of the name suitable for use in a file name
   transformation : function float -> float
   \tSome mapping R->R representing how digital competence is affected by
   \tthis manipulation
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
      self.name = name
      self.name_for_file = _trim_for_filename(self.name)
      self.transformation = transformation
      return
      
class background:
   """
   This represents something that can be expected to affect the results of
   the participants in the study, but which cannot be directly controlled
   by the experimenters. For example, it is possible that the results can
   be affected by whether the participants are native speakers of the
   language that the course is given in.
   
   When simulating a study, some backgrounds are assumed to be known and
   some are assumed to be unknown. One goal of these simulations is to get
   an idea of how much background variables interfere with our results.

   Attributes
   ----------
   name : str
   \tDescription of the background
   name_for_file : str
   \tRendition of the name suitable for use in a file name
   pre_transformation : function float->float
   \tThe effect that the background has on the digital skills of the
   \tparticipants prior to the study
   post_transformation : function float->float
   \tThe effect that the background has on the acquisition of digital
   \tskills during the course of the study
   fraction : float
   \tThe probability that a given participant is affected by the
   background
   """
   
   def __init__(self, name, pre_transformation, post_transformation, fraction):
      """
      Parameters
      ----------
      name : str
      \tDescribed under attributes
      pre_transformation : function float->float
      \tDescribed under attributes
      post_transformation : function float->float
      \tDescribed under attributes
      fraction : float
      \tDescribed under attributes
      """
      self.name = name
      self.name_for_file = _trim_for_filename(self.name)
      self.pre_transformation = pre_transformation
      self.post_transformation = post_transformation
      self.fraction = fraction
      return
      
class skill_boundaries:
   """
   This is used in one possible test for evaluating the effectiveness of a
   course module. We define two boundaries, such that participants with
   digital competence below the lower boundary are considered to have poor
   skills and those above the higher boundary have good skills. The bound-
   aries can be identical, but do not need to be.
   
   A skill_boundaries object should be given to a study object, where the
   boundaries will be placed on the same ordinal scale as the participants'
   skills before and after the module. This is then used to calculate a
   quality for each different version of the modules, defined as the
   probability that a person starting with poor skills will have good
   skills after taking the course module.
   
   Optionally, it is possible to also supply a minimal difference in
   quality which we consider to be practically significant.
   
   Attributes
   ----------
   poor : float
   \tThe level below which participants are considered to have low digital
   \tcompetence
   good : float
   \tThe level above which participants are considered to have high
   \tdigital competence
   poor_ordinal : int
   \tThe level for low digital competence, placed on an ordinal scale
   \ttogether with the skills of a group of participants
   good_ordinal : int
   \tThe level for high digital competence, placed on an ordinal scale
   \ttogether with the skills of a group of participants
   minimum_quality_difference : float
   \tThe difference in quality which we consider to be practically signif-
   \ticant. This defaults to zero, meaning that any different is taken to
   \tbe practically significant.
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
         print("Poor digital skills are higher than good!")
         print("Assuming you meant the other way around...")
         poor, good = good, poor
      self.poor = poor
      self.good = good
      self.poor_ordinal = np.nan
      self.good_ordinal = np.nan
      self.minimum_quality_difference = minimum_quality_difference
      return

class participants:
   """
   This represents the people participating in the study, each of whom is
   taking some version of the module intended to improve their digital
   competence.
  
   If there are known background variables the participants are divided
   into smaller groups where all members are affected in the same way.
  
   Attributes
   ----------
   n : int
   \tThe number of participants in the study
   initial_distribution : function int->float ndarray
   \tThe statistical distribution that describes the digital competence of
   \tthe participants prior to taking the course
   known_backgrounds : list of background
   \tBackgrounds that affect some subset of participants, and which are
   \tassumed to be known to the experimenters
   unknown_backgrounds : list of background
   \tBackgrounds that affect some subset of participants, and which are
   \tnot known to the experimenters
   all_backgrounds : list of background
   \tList containing both the known and unknown backgrounds
   background_flags : dict of bool ndarrays
   \tDictionary containing arrays stating which participants are
   \taffected by which backgrounds
   subgroups : dict of int ndarrays
   \tDictionary containing the indices of the participants in each
   \tsubgroup
   digicomp_pre : float ndarray
   \tThe digital competence of the participants before taking the module
   digicomp_post : float ndarray
   \tThe digital competence of the participants after taking the module.
   \tThis is initially set to nan, and should be set to definite values by
   \tthe class study.
   digicomp_delta : float ndarray
   \tThe change in digital competence of the participants as a result of
   \ttaking the module.
   \tThis is initially set to nan, and should be set to definite values by
   \tthe class study.
   """
   def __init__(self, n, initial_distribution, known_backgrounds = [], unknown_backgrounds = []):
      """
      Parameters
      ----------
      n : int
      \tDescribed under attributes
      initial_distribution : function int->float ndarray
      \tDescribed under attributes
      
      Optional parameters
      -------------------
      known_backgrounds : list of background
      \tDescribed under attributes
      unknown_backgrounds : list of background
      \tDescribed under attributes
      """
      self.n = n
      self.initial_distribution = initial_distribution
      self.known_backgrounds = known_backgrounds
      self.unknown_backgrounds = unknown_backgrounds
      self.all_backgrounds = self.known_backgrounds + self.unknown_backgrounds
      
      self.background_flags = {}
      for background in self.all_backgrounds:
         self.background_flags[background.name] = rd.random(self.n) < background.fraction
         
      self.subgroups = self._define_subgroups()
         
      self.digicomp_pre = self._calculate_digicomp_pre()
      self.digicomp_post = np.zeros(n) * np.nan
      self.digicomp_delta = np.zeros(n) * np.nan
      
      self.digicomp_pre_ordinal = np.zeros(n) * np.nan
      self.digicomp_post_ordinal = np.zeros(n) * np.nan
      # By definition, there is no digicomp_delta_ordinal
      return
   
   def _calculate_digicomp_pre(self):
      """
      Calculate the digital competence prior to the start of the course,
      using the initial distribution and adding the relevant background
      effects
      """
   
      digicomp_pre = self.initial_distribution(self.n)
      for background in self.all_backgrounds:
          digicomp_pre[self.background_flags[background.name]] = background.pre_transformation(digicomp_pre[self.background_flags[background.name]])
      return digicomp_pre
   
   def _define_subgroups(self):
      """
      Divide the participants into subgroups where the members are subject
      to the same known backgrounds
      """
      
      subgroups = {}
      subgroup_names = set([])
      for i in range(self.n):
         participant_flags = []
         for background in self.known_backgrounds:
            if self.background_flags[background.name][i]:
               participant_flags.append(background.name)
         subgroup_name = ", ".join(participant_flags)
         if subgroup_name == "":
            subgroup_name = "no background"
         
         if not (subgroup_name in subgroup_names):
            subgroups[subgroup_name] = []
            subgroup_names.add(subgroup_name)
         subgroups[subgroup_name].append(i)
      for subgroup_name in subgroup_names:
         subgroups[subgroup_name] = np.asarray(subgroups[subgroup_name])
      return subgroups
   
   def describe(self):
      """
      Gives a summary of the most important facts about the participants
      """
      print("Description of the participants:\n")
      print("There {} {} participant{}".format(_is_are(self.n), self.n, _plural_ending(self.n)))
      for wording, background_dict in [("known", self.known_backgrounds), ("unknown", self.unknown_backgrounds)]:
         n_backgrounds = len(background_dict)
         print("\nThere {} {} background{} {} to the experimenters".format(_is_are(n_backgrounds), n_backgrounds, _plural_ending(n_backgrounds), wording))
         for background in background_dict:
            n_affected = np.sum(self.background_flags[background.name])
            print("{}Background: {}".format(_indent(1), background.name))
            print("{}Affects {} participant{}".format(_indent(2), n_affected, _plural_ending(n_affected)))
            print("{}Which makes up {:.2f} of total".format(_indent(2), n_affected / self.n))
      
      if len(self.known_backgrounds) > 0:
         print("\nThe known backgrounds require splitting the group into the following subgroups")
         for subgroup_name, subgroup_members in self.subgroups.items():
            n_members = len(subgroup_members)
            print("{}'{}'".format(_indent(1), subgroup_name))
            print("{}Has {} member{}".format(_indent(2), n_members, _plural_ending(n_members)))
            print("{}Out of these, some may be affected by unknown backgrounds:".format(_indent(2)))
            for background in self.unknown_backgrounds:
               print("{}{}: {}".format(_indent(3), background.name, sum(self.background_flags[background.name][subgroup_members])))
         print("\n")
      return

class study:
   """
   This represents a test run of a course module, in which data about the
   participants' digital competence is collected before and after taking
   the module.
   
   Attributes
   ----------
   name : string
   \tName of the study. Used for filenames when plotting.
   participants : participants
   \tThe people taking the course
   default_effect : function float->float
   \tThe effect that the default version of the course has on the digital
   \tskills of the participants
   manipulations : list of manipulations
   \tThe manipulations that are tried out on the participants
   n_manipulations : int
   \tThe number of manipulations that are carried out
   manipulation_flags : dict of bool ndarrays
   \tDictionary containing arrays stating which participants are affected
   \tby which manipulations
   all_flags : dict of bool ndarrays
   \tDictionary containing both the manipulation flags and the boundary
   \tflags of the participants
   manipulation_groups : dict of int ndarrays
   \tDictionary containing the indices of the participants that are
   \taffected by each manipulation
   bounds : skill_boundaries
   \tBoundaries defining poor and good digital skill, as defined by this
   \tstudy
   boundary_tests_run : bool
   \tWhether the tests implied by the bounds have been run
   """
   
   def __init__(self, name, participants, default_effect, manipulations, bounds = None, combined_manipulations = []):
      """
      Parameters
      ----------
      name : string
      \tDescribed under attributes
      participants : participants
      \tDescribed under attributes
      default_effect : function float->float
      \tDescribed under attributes
      manipulations : list of manipulation
      \tDescribed under attributes
   
      Optional parameters
      -------------------
      bounds : skill_boundaries
      \tDescribed under attributes
      combined_manipulations :
      \tTo be implemented
      """
      self.name = name
      self.participants = participants
      self.default_effect = default_effect
      self.manipulations = manipulations
      self.bounds = bounds
      self.boundary_tests_run = False
      
      self.n_manipulations = len(self.manipulations)
      self.manipulation_flags = self._set_manipulation_flags()
      self.all_flags = {**self.manipulation_flags, **self.participants.background_flags}
      
      # Define manipulation groups
      self.manipulation_groups = self._define_manipulation_groups()
      
      self.sanity_checks = {}
      self.measured_results = {}
      self.bounds_ordinal = {}
      
      self.plot_folder = None
      
      self._qk_samples = self.participants.n * 10
      self._qk_sample_width = 1 / self._qk_samples
      self._Qki_range = np.linspace(0.0, 1.0, num=self._qk_samples)
      self._dk_samples = 2 * self._qk_samples - 1
      self._Dk_range = np.linspace(-1.0, 1.0, num=self._dk_samples)
      return
      
   def _set_manipulation_flags(self):
      n_manipulations = len(self.manipulations)

      manipulation_flags = {}
      for i in range(n_manipulations):
         flags = np.zeros(self.participants.n, dtype = np.bool)
         manipulation = self.manipulations[i]

         for subgroup_name, subgroup_indices in self.participants.subgroups.items():

            n_blocks = 2**(i+1)
            block_exact_breakpoints = np.linspace(0, len(subgroup_indices), 2**(i+1) + 1)
            block_breakpoints = np.rint(block_exact_breakpoints).astype(int)
         
            for start, stop in zip(block_breakpoints[0:-2:2], block_breakpoints[1:-1:2]):
               flags[subgroup_indices[start:stop]] = True
            manipulation_flags[manipulation.name] = flags
      return manipulation_flags

   def _define_manipulation_groups(self):

      # Maybe combine this function with define_subgroups in class participants?
      
      manipulation_groups = {}
      manipulation_group_names = set([])
      for i in range(self.participants.n):
         participant_flags = []
         for manipulation in self.manipulations:
            if self.manipulation_flags[manipulation.name][i]:
               participant_flags.append(manipulation.name)
         manipulation_group_name = ", ".join(participant_flags)
         if manipulation_group_name == "":
            manipulation_group_name = "no manipulation"
         
         if not (manipulation_group_name in manipulation_group_names):
            manipulation_groups[manipulation_group_name] = []
            manipulation_group_names.add(manipulation_group_name)
         manipulation_groups[manipulation_group_name].append(i)
      for manipulation_group_name in manipulation_group_names:
         manipulation_groups[manipulation_group_name] = np.asarray(manipulation_groups[manipulation_group_name])
      return manipulation_groups

   def describe(self):
      """
      Gives a summary of the most important facts about the study, which
      are assumed to be known prior to the study being carried out.
      """
   
      print("Description of the study itself:\n")
      print("There {} {} participant{}".format(_is_are(self.participants.n), self.participants.n, _plural_ending(self.participants.n)))
      print("We are testing {} manipulation{}:".format(self.n_manipulations, _plural_ending(self.n_manipulations)))
      for manipulation in self.manipulations:
         print("{}{}".format(_indent(1), manipulation.name))
         
      n_backgrounds = len(self.participants.known_backgrounds)
      if n_backgrounds > 0:
         print("\nThere {} {} known background{}:".format(_is_are(n_backgrounds), n_backgrounds, _plural_ending(n_backgrounds)))
         for background in self.participants.known_backgrounds:
            print("{}{}".format(_indent(1), background.name))
         print("Hence, the participants are split into {} subgroups\n".format(len(self.participants.subgroups)))

      n_unknown_backgrounds = len(self.participants.unknown_backgrounds)
      if n_unknown_backgrounds > 0:
         print("There {} {} unknown background{}:".format(_is_are(n_unknown_backgrounds), n_unknown_backgrounds, _plural_ending(n_unknown_backgrounds)))
         for background in self.participants.unknown_backgrounds:
            print("{}{}".format(_indent(1), background.name))
         print("This may affect the study\n")
            
      print("Group membership:")
      for subgroup_name, subgroup_members in self.participants.subgroups.items():
         n_members = len(subgroup_members)
         print("{}Group '{}' has {} member{}".format(_indent(1), subgroup_name, n_members, _plural_ending(n_members)))
         # Maybe move this?
         subgroup_members = set(subgroup_members)
         for manipulation_group_name, manipulation_group_members in self.manipulation_groups.items():
            manipulation_members = set(manipulation_group_members)
            subgroup_manipulation = subgroup_members.intersection(manipulation_members)
            print("{}Manipulation group '{}' has {} members".format(_indent(2), manipulation_group_name, len(subgroup_manipulation)))
      print("\n")
      
   def _apply_manipulations(self):
      self.participants.digicomp_post = self.participants.digicomp_pre + self.default_effect(self.participants.digicomp_pre)
      
      for manipulation in self.manipulations:
         self.participants.digicomp_post[self.manipulation_flags[manipulation.name]] = manipulation.transformation(self.participants.digicomp_post[self.manipulation_flags[manipulation.name]])
        
      for background in self.participants.all_backgrounds:
         self.participants.digicomp_post[self.participants.background_flags[background.name]] = background.post_transformation(self.participants.digicomp_post[self.participants.background_flags[background.name]])
         
      self.participants.digicomp_delta = self.participants.digicomp_post - self.participants.digicomp_pre

      data_to_ordinalise = [self.participants.digicomp_pre, self.participants.digicomp_post]
      if self.bounds != None:
         data_to_ordinalise += [np.asarray([self.bounds.poor]), np.asarray([self.bounds.good])]
      ordinal_data = _ordinalise_many(data_to_ordinalise)
      self.participants.digicomp_pre_ordinal = ordinal_data[0]
      self.participants.digicomp_post_ordinal = ordinal_data[1]
      if self.bounds != None:
         self.bounds.poor_ordinal = ordinal_data[2]
         self.bounds.good_ordinal = ordinal_data[3]
      return
   
   def _do_sanity_checks(self):
      """
      These tests make use of information that is assumed to be hidden from
      the experimenters. Hence, they should only be used to test the internal
      consistency of a model study.
      """
      self.sanity_checks["average differences"] = {}
      for manipulation in self.manipulations:
         average_result_with_manipulation = np.mean(self.participants.digicomp_post[self.manipulation_flags[manipulation.name]])
         average_result_without_manipulation = np.mean(self.participants.digicomp_post[np.invert(self.manipulation_flags[manipulation.name])])
         self.sanity_checks["average differences"][manipulation.name] = average_result_with_manipulation - average_result_without_manipulation
      return
   
   def _compare_flagged(self, flags, results):
      treatment_group = results[flags]
      control_group = results[np.invert(flags)]
      
      statistics = {}
      statistics['treatment group median'] = np.median(treatment_group)
      statistics['control group median'] = np.median(control_group)
      s, p, m, table = st.median_test(treatment_group, control_group)
      statistics['median test test statistic'] = s
      statistics['median test p-value'] = p
      statistic, pvalue = st.mannwhitneyu(treatment_group, control_group)
      statistics['Mann-Whitney U rank test test statistic'] = statistic
      statistics['Mann-Whitney U rank test p-value'] = pvalue
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
         print("Out of {} calculated values of qki {} are nan".format(self._qk_samples, nan_qki))
         print("Skipping boundary tests")
         return

      qki_mass = qki * self._qk_sample_width
      if np.abs(sum(qki_mass) - 1) > 0.01:
         print("Problem in calculation!")
         print("Probability density function not well normalised")
      dictionary['Probabilities of qualities'] = qki
      dictionary['log-probabilities of qualities'] = log_qki
      dictionary['Probability mass per sampled quality'] = qki_mass
      dictionary['Peak of Qki'] = self._Qki_range[np.argmax(qki)]
      dictionary['Percentiles of qki'] = self._make_percentiles(self._Qki_range, qki_mass)
      dictionary['Median of qki'] = dictionary['Percentiles of qki'][50.0]
      return
      
   def _fill_dictionary_with_qk_and_dk(self, dictionary, practical_significance_cutoff):
      qktreat = dictionary['treatment group']['Probability mass per sampled quality']
      qkcont = dictionary['control group']['Probability mass per sampled quality']
      dk = np.convolve(qktreat, np.flip(qkcont))
      
      dictionary['Range of quality differences'] = self._Dk_range
      dictionary['Probabilities of quality differences'] = dk
      dictionary['Peak of dk'] = self._Dk_range[np.argmax(dk)]
      dictionary['Percentiles of dk'] = self._make_percentiles(self._Dk_range, dk)
      dictionary['Median of dk'] = dictionary['Percentiles of dk'][50.0]
      PDl0 = np.sum(dk[:self._qk_samples])
      PDg0 = np.sum(dk[self._qk_samples+1:])
      dictionary['Probability that treatment group does better than control group'] = PDg0
      dictionary['Probability that treatment group does worse than control group'] = PDl0

      # Look very closely at this
      cutoff = int(practical_significance_cutoff / self._qk_sample_width)

      PDll0 = np.sum(dk[:self._qk_samples - cutoff])
      PDap0 = np.sum(dk[self._qk_samples - cutoff:self._qk_samples + cutoff])
      PDgg0 = np.sum(dk[self._qk_samples + cutoff:])
      dictionary['Probability that treatment group does much better than control group'] = PDgg0
      dictionary['Probability that treatment group does much worse than control group'] = PDll0
      dictionary['Probability that treatment group does about as well as control group'] = PDap0
      return dictionary
   
   ### Functions specific to the boundary tests

   def _logL_bounds(self, Qki, nl, nlh):
      """
      The log-probability over the quality, where quality is defined as the
      probability that a person who initially had low digital competence will
      have high digital competence after the course module. This requires
      definition of bounds for low and high quality when creating the study.
      """
      with np.errstate(divide = 'ignore'):
         log_qki = nlh * np.log(Qki) + (nl - nlh) * np.log(1 - Qki) - logB(nlh + 1, nl - nlh + 1)
      return log_qki
      
   def _boundary_tests(self, pre, post):
      poor = self.bounds.poor_ordinal
      good = self.bounds.good_ordinal   
      
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
      
   def _boundary_test_total(self, participants):
      """
      Runs boundary tests for the entire module, to check whether it has any
      noteworthy effect to begin with.
      """
      return self._boundary_tests(participants.digicomp_pre_ordinal, participants.digicomp_post_ordinal)

   def _boundary_test_background_or_manipulation(self, flags, participants):
      """
      Runs boundary tests with respect to some background or manipulation.
      """
      treatment_group_pre = participants.digicomp_pre_ordinal[flags]
      control_group_pre = participants.digicomp_pre_ordinal[np.invert(flags)]
      treatment_group_post = participants.digicomp_post_ordinal[flags]
      control_group_post = participants.digicomp_post_ordinal[np.invert(flags)]
      
      poor = self.bounds.poor_ordinal
      good = self.bounds.good_ordinal
      
      boundary_tests = {'treatment group':{}, 'control group':{}}
      for text, pre, post in [('treatment group', treatment_group_pre, treatment_group_post), ('control group', control_group_pre, control_group_post)]:
         boundary_tests[text] = self._boundary_tests(pre, post)
      
      self._fill_dictionary_with_qk_and_dk(boundary_tests, self.bounds.minimum_quality_difference)
      self.boundary_tests_run = True
      return boundary_tests
      
   ### Functions specific to the Bayesian median tests
      
   def _logL_median(self, Qki, nki, n_good):
      with np.errstate(divide = 'ignore'):
         log_qki = n_good * np.log(Qki) + (nki - n_good) * np.log(1 - Qki) - logB(n_good + 1, nki - n_good + 1)
      return log_qki
      
   def _median_tests(self, control, treat):
      median = np.median(np.concatenate([control, treat]))
      
      median_test_result = {'control group':{}, 'treatment group':{}}
      median_test_result['control group']['total members'] = len(control)
      median_test_result['control group']['members below median'] = np.count_nonzero(control < median)
      median_test_result['control group']['members above median'] = np.count_nonzero(control > median)
      median_test_result['treatment group']['total members'] = len(treat)
      median_test_result['treatment group']['members below median'] = np.count_nonzero(treat < median)
      median_test_result['treatment group']['members above median'] = np.count_nonzero(treat > median)

      for group, group_name in [(control, 'control group'), (treat, 'treatment group')]:
         n_good = median_test_result[group_name]['members above median']
         n_ki = median_test_result[group_name]['total members']
         log_qki = self._logL_median(self._Qki_range, n_ki, n_good)
         self._calculate_qki_and_fill_in_dict(log_qki, median_test_result[group_name])
      return median_test_result
      
   def _median_test_total(self, participants):
      """
      Runs median tests for the entire module. This tests whether the skills
      before or after taking the module are higher than the median skill for
      both before and after taking the module.
      
      Note that this compares participants against a group that includes
      themselves at another point in time.
      """
      median_tests = {}
      median_tests['after module'] = self._median_tests(participants.digicomp_pre_ordinal, participants.digicomp_post_ordinal)
      median_tests['before module'] = self._median_tests(participants.digicomp_post_ordinal, participants.digicomp_pre_ordinal)
      self._fill_dictionary_with_qk_and_dk(median_tests['after module'], 0.1) 
      return median_tests
      
   def _median_test_background_or_manipulation(self, flags, participants):
      """
      This tests how likely it seems to be that a participant in either the
      control or treatment group does better than the median for the control
      and treatment groups together.
      """
      
      treatment_group_pre = participants.digicomp_pre_ordinal[flags]
      control_group_pre = participants.digicomp_pre_ordinal[np.invert(flags)]
      treatment_group_post = participants.digicomp_post_ordinal[flags]
      control_group_post = participants.digicomp_post_ordinal[np.invert(flags)]
      
      median_tests = {}
      for text, control, treat in [('before module', control_group_pre, treatment_group_pre), ('after module', control_group_post, treatment_group_post)]:
         median_tests[text] = self._median_tests(control, treat)
         self._fill_dictionary_with_qk_and_dk(median_tests[text], 0.1) # Fix magic number
      return median_tests
   
   ### Functions that run the tests above
   
   def _do_tests(self):
      """
      These are the tests that experimentalists could to, making use of the
      information that they would have access to.
      """
      self.measured_results = {}
      self.measured_results['quick tests'] = {}
      for manipulation in self.manipulations:
         self.measured_results['quick tests'][manipulation.name] = self._compare_flagged(self.manipulation_flags[manipulation.name], self.participants.digicomp_post_ordinal)
      for background in self.participants.known_backgrounds:
         self.measured_results['quick tests'][background.name] = self._compare_flagged(self.participants.background_flags[background.name], self.participants.digicomp_post_ordinal)
         
      self.measured_results['quick tests']['total'] = {}
      self.measured_results['quick tests']['total']['pre-course median'] = np.median(self.participants.digicomp_pre_ordinal)
      self.measured_results['quick tests']['total']['post-course median'] = np.median(self.participants.digicomp_post_ordinal)
      n_improved = np.sum(self.participants.digicomp_post_ordinal > self.participants.digicomp_pre_ordinal)
      with np.errstate(divide = 'ignore'):
         pvalue = st.binom_test(n_improved, self.participants.n)
      self.measured_results['quick tests']['total']['sign test p-value'] = pvalue

      self.measured_results['median tests'] = {}
      self.measured_results['median tests']['total'] = self._median_test_total(self.participants)
      for manipulation in self.manipulations:     
         self.measured_results['median tests'][manipulation.name] = self._median_test_background_or_manipulation(self.manipulation_flags[manipulation.name], self.participants)
      for background in self.participants.known_backgrounds:
         self.measured_results['median tests'][background.name] = self._median_test_background_or_manipulation(self.participants.background_flags[background.name], self.participants)
         
      if self.bounds != None:
         self.measured_results['boundary tests'] = {}
         self.measured_results['boundary tests']['total'] = self._boundary_test_total(self.participants)
         for manipulation in self.manipulations:
            self.measured_results['boundary tests'][manipulation.name] = self._boundary_test_background_or_manipulation(self.manipulation_flags[manipulation.name], self.participants)
         for background in self.participants.known_backgrounds:
            self.measured_results['boundary tests'][background.name] = self._boundary_test_background_or_manipulation(self.participants.background_flags[background.name], self.participants)
      return
   
   ### Functions for outputting results
   
   def summarise_results(self):
      """
      Summarise the findings that the experimentalists have at the end of the
      study.
      """
      def print_poor_to_high(group_name, group_data, base_indent):
         print("{}In {}, out of {} members with poor skills {} acquire good skills".format(_indent(base_indent), group_name, group_data['members with initially poor skills'], group_data['members moving from poor to good skills']))
         print("{}Quality estimated to be: {:.2f}".format(_indent(base_indent + 1), group_data['Median of qki']))
         print("{}One sigma bounds at: {:.2f} - {:.2f}".format(_indent(base_indent + 1), group_data['Percentiles of qki'][15.87], group_data['Percentiles of qki'][84.13]))
         print("{}Two sigma bounds at: {:.2f} - {:.2f}".format(_indent(base_indent + 1), group_data['Percentiles of qki'][2.28], group_data['Percentiles of qki'][97.72]))
         return
         
      def print_above_median(group_name, group_data, base_indent):
         print("{}In {}, out of {} members {} end up above median".format(_indent(base_indent), group_name, group_data['total members'], group_data['members above median']))
         print("{}Quality estimated to be: {:.2f}".format(_indent(base_indent + 1), group_data['Median of qki']))
         print("{}One sigma bounds at: {:.2f} - {:.2f}".format(_indent(base_indent + 1), group_data['Percentiles of qki'][15.87], group_data['Percentiles of qki'][84.13]))
         print("{}Two sigma bounds at: {:.2f} - {:.2f}".format(_indent(base_indent + 1), group_data['Percentiles of qki'][2.28], group_data['Percentiles of qki'][97.72]))
         return
      
      def print_dk_permutations(dk_dict, base_indent):
         for descriptor in ['Probability that treatment group does better than control group', 'Probability that treatment group does worse than control group','Probability that treatment group does much better than control group','Probability that treatment group does much worse than control group','Probability that treatment group does about as well as control group']:
            print("{}{}: {:.2f}".format(_indent(base_indent), descriptor, dk_dict[descriptor]))
         return
      
      def print_total_median(dk_dict, base_indent):
         print("{}After taking the course module, {} out of {} members are above the total median".format(_indent(base_indent), dk_dict['treatment group']['members above median'], dk_dict['treatment group']['total members']))
         print("{}'Quality difference' before and after module estimated to be: {:.2f}".format(_indent(base_indent), dk_dict['Median of dk']))
         print("{}One sigma bounds at: {:.2f} - {:.2f}".format(_indent(base_indent), dk_dict['Percentiles of dk'][15.87], dk_dict['Percentiles of dk'][84.13]))
         print("{}Two sigma bounds at: {:.2f} - {:.2f}".format(_indent(base_indent), dk_dict['Percentiles of dk'][2.28], dk_dict['Percentiles of dk'][97.72]))
         print_dk_permutations(dk_dict, base_indent)
         return
      
      def print_quality_difference(dk_dict, base_indent):
         print("{}Comparing control group and test group".format(_indent(base_indent)))
         print("{}Quality difference estimated to be: {:.2f}".format(_indent(base_indent + 1), dk_dict['Median of dk']))
         print("{}One sigma bounds at: {:.2f} - {:.2f}".format(_indent(base_indent + 1), dk_dict['Percentiles of dk'][15.87], dk_dict['Percentiles of dk'][84.13]))
         print("{}Two sigma bounds at: {:.2f} - {:.2f}".format(_indent(base_indent + 1), dk_dict['Percentiles of dk'][2.28], dk_dict['Percentiles of dk'][97.72]))
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
      
      for variation, description in [(self.manipulations, 'manipulation'), (self.participants.known_backgrounds, 'background')]:
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
  

   def plot_participants(self):
      """
      Plot group membership of all participants.
      """
      
      def plot_flags(flags, name):
         side = int(np.ceil(np.sqrt(self.participants.n)))
         i = np.arange(self.participants.n)
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
         sorted_1, dummy, sorted_2 = zip(*sorted(zip(flags_1, range(self.participants.n), flags_2)))
         side = int(np.ceil(np.sqrt(self.participants.n)))
         i = np.arange(self.participants.n)
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
      
      for name_1, flags_1 in self.all_flags.items():
         plot_flags(flags_1, name_1)
         for name_2, flags_2 in self.all_flags.items():
            plot_group_subgroup(flags_1, flags_2, name_1, name_2)
      return


   def plot_results(self):
      """
      Plot the results of the study. This includes.
      
      - The estimated quality of the teaching module with and without each
      manipulation
      
      - The logarithm of the above. This can be interesting since the
      distributions often drop off exponentially, meaning that normally only
      a sharp peak is visible.
      
      - The estimated difference between the versions of the teaching module
      with and without each manipulation
      """
      
      def plot_quality(test_name, test_data):
         plt.clf()
         plt.tight_layout()
         plt.plot(self._Qki_range, test_data['control group']['Probabilities of qualities'], label = 'Control')
         plt.plot(self._Qki_range, test_data['treatment group']['Probabilities of qualities'], label = 'Treatment')
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
         plt.plot(self._Dk_range, test_data['Probabilities of quality differences'], label = 'Difference')
         plt.xlim(-1, 1)
         plt.axvline(x = 0.0, c = 'k')
         plt.axvline(x = self.bounds.minimum_quality_difference, linestyle = '--', c = 'k')
         plt.axvline(x =-self.bounds.minimum_quality_difference, linestyle = '--', c = 'k')
         plt.savefig('./{}/ill_{}_{}_{}_{}_difference.png'.format(self.plot_folder, self.name.replace(' ', '_'), test_name, description, choice.name.replace(' ', '_')))
         return
      
      if self.plot_folder == None:
         print("You need to specify a relative path to a folder for the plots")
         return
   
      if not os.path.isdir('./{}'.format(self.plot_folder)):
         print("This needs to be run in the same directory as a directory named '{}'".format(self.plot_folder))
         return

      for variation, description in [(self.manipulations, 'manipulation'), (self.participants.known_backgrounds, 'background')]:
         for choice in variation:
            plot_quality('mtest', self.measured_results['median tests'][choice.name]['after module'])

            if self.boundary_tests_run:
               plot_quality('btest', self.measured_results['boundary tests'][choice.name])
      return
      
   def run_study(self):
      """
      Simulate the participants taking their various versions of the course,
      increasing in digital competence as they do so. Then simulate the
      experimenters studying the results.
      """
      
      self._apply_manipulations()
      self._do_sanity_checks()
      self._do_tests()
      return
   
