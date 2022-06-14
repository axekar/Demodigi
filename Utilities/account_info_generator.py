"""
This module was written for the ESF-financed project Demokratisk
Digitalisering (DD). The project is a collaboration between
Arbetsförmedlingen (AF) and Kungliga Tekniska Högskolan (KTH). The
purpose of the project is to increase the digital competence - as
defined at https://ec.europa.eu/jrc/en/digcomp - of people working at
Arbetsförmedlingen, and by extension also job seekers. This will be
done by learning modules at KTH using OLI-Torus.

--- About this Python module ---

This module is intended to create user IDs and passwords for the people
who will be taking the learning modules. The user IDs need to be easy
to remember, while not being tied to the actual person in any way. The
passwords need to be secure, while also being easy to remember in case
the users to not have password managers.

When generating user IDs, I will take the following approach:

 - It should be a Swedish adjective followed by a noun, neither one of
   which is offensive.

When generating passwords, I will take the following approach:

 - It should consist of five Swedish words, separated by spaces

 - It should consist of only lowercase letters. We will not do the
   mixing of cases, numbers and special characters that is typically
   recommended, since that makes passwords harder to remember without
   actually making them much more secure.
   
As far as I have been able to figure out, this is the current best
practise for generating passwords. The more commonly recommended method
of mixing upper- and lowercase with numbers and special characters does
not inherently increase password entropy: With a random selection of
symbols you can get any entropy you want by choosing sufficiently many
symbols and having a sufficiently large alphabet of symbols. This being
the case, for a given entropy this method gives much more easily
memorable passwords than that method would. For a popular explanation
of the underlying mathematics, see https://xkcd.com/936/
   
--- IMPORTANT NOTICE ---

The data that comes out of this module must be handled with some care.
To begin with, the passwords must obviously not be kept anywhere that
can be accessed by anyone except project members that have the relevant
privileges. In addition, the information about which user ID
corresponds to which real-world person is also secret, and must be
stored where only we can access it.

Written by Alvin Gavel,

https://github.com/Alvin-Gavel/Demodigi
"""

import base64
import hashlib as hl
import secrets
import string
import sys

import numpy as np
import pandas as pd

generic_warning = "NOTE: This information must be stored where it is not accessible to anyone except project members who have been so authorised."

def read_wordlist(file_path):
   """
   Read a file of words, assuming each line has one word on it
   """
   f = open(file_path, encoding='latin-1')
   words = [word.strip().lower() for word in f]
   f.close()
   return words
   
   
class password_generator:
   """
   This generates passwords consisting of n characters chosen with uniform
   probability. What the characters are depends on the choice of method:
   
   - alphabetic (lower): Lowercase letters from the English alphabet

   - alphabetic (upper): Uppercase letters
   
   - alphabetic: Upper- and lowercase letters

   - alphanumeric: Upper- and lowercase letters, together with numerals
   
   - mixed: Upper- and lowercase letters, numerals and special characters
   
   - XKCD: In this case the characters are entire words, which requires a
     wordlist to be supplied.
     
   Not that the 'XKCD' method is the only one I actually recommend. The
   others are there only in case an inflexible password policy requires us
   to use them, or to allow quickly demonstrating why they are so bad. For
   a simply explanation of the method, see https://xkcd.com/936/
   """
   def __init__(self, length, method, wordlist = None):
      """
      Parameters
      ----------
      length : int
      \tThe number of characters in a password - where a 'character' may be
      \tan entire word
      method : str
      \tThe method used for generating a password
      Optional parameters:
      -------------------
      wordlist : list of str
      \tWhen using the 'xkcd' method, this is a list of words used to
      \tgenerate the passwords
      """
      self.length = length
      if method.lower() == 'xkcd':
         self.alphabet = wordlist
         self.delimiter = ' '
      elif method.lower() == 'alphabetic (lower)':
         self.alphabet = string.ascii_lowercase
         self.delimiter = ''
      elif method.lower() == 'alphabetic (upper)':
         self.alphabet = string.ascii_uppercase
         self.delimiter = ''
      elif method.lower() == 'alphabetic':
         self.alphabet = string.ascii_letters
         self.delimiter = ''
      elif method.lower() == 'alphanumeric':
         self.alphabet = string.ascii_letters + string.digits
         self.delimiter = ''
      elif method.lower() == 'mixed':
         self.alphabet = string.ascii_letters + string.digits + string.punctuation
         self.delimiter = ''
      else:
         print('Cannot recognise method')
      
      self.n_words = len(self.alphabet)
      self.n_possible_passwords = self.n_words**length
      self.entropy = np.log2(float(self.n_possible_passwords))
      return
      
   def generate_password(self):
      """
      Generate one password consisting of a certain number of symbols.
      """
      return self.delimiter.join(secrets.choice(self.alphabet) for i in range(self.length))
                   
   def print_info(self):
      """
      Gives some basic information about the method for generating passwords
      """
      print("The character list has {} entries".format(self.n_words))
      print("This permits about {:.0e} unique passwords, chosen with uniform probability".format(self.n_possible_passwords))
      print("This corresponds to {:.0f} bits of entropy".format(self.entropy))
      return

class ID_generator:
   """
   This generates IDs consisting of one adjective followed by one noun,
   which are assumed to be in the directory Word_lists.
   """
   def __init__(self):
      self.adjective_list = pd.read_csv('Word_lists/Adjectives.csv')
      self.noun_list = pd.read_csv('Word_lists/Nouns.csv')
      return
      
   def generate_ID(self):
      """
      Generate one ID consisting of an adjective followed by a noun. This
      takes account of the fact that in Swedish, the form the adjective takes
      depends on the grammatical gender of the noun. 
      """
      noun, gender = secrets.choice(list(zip(self.noun_list['ord'], self.noun_list['genus'])))
      adjective = secrets.choice(self.adjective_list[gender])
      return '{} {}'.format(adjective, noun)


class participant_list:
   """
   This represents a list of people taking the learning module.
   
   Attributes
   ----------
   ID_generator : ID_generator object
   \tGenerates IDs in an adjective-noun format
   password_wordlist : list of str
   \tList of words used when generating passwords
   password_generator : password_generator
   \tGenerates passwords in the format of words separated by spaces
   participant_data : pandas dataframe
   \tData describing the participants in the learning module
   account_data : pandas dataframe
   \tData describing the Canvas accounts of the participants
   sharepoint_data : pandas dataframe
   \tData to be passed on to the SharePoint robot, which will pass o
   n_participants : int
   \tThe number of participants
   participant_info_read : bool
   \tWhether info about the participants has been read
   """
   def __init__(self, password_wordlist, password_length = 5):
      """
      Parameters
      ----------
      password_wordlist : list of str
      \tDescribed under attributes

      Optional parameters
      -------------------
      password_length : int
      \tThe number of symbols that will make up a password
      """
      self.ID_generator = ID_generator()
      self.password_wordlist = password_wordlist
      self.password_generator = password_generator(password_length, 'xkcd', wordlist = self.password_wordlist)
      self.participant_data = pd.DataFrame(columns = ['name', 'email'])
      self.account_data = pd.DataFrame(columns = ['user_id', 'login_id', 'password', 'status'])
      self.sharepoint_data = pd.DataFrame(columns = ['name', 'email', 'user_id', 'password'])
      self.n_participants = np.nan
      self.participant_info_read = False
      return
      
   ### Functions for getting data about the actual participants
      
   def simulate_participant_data(self, n_participants):
      """
      Create fictional participants, to test that the code works
      """
      self.n_participants = n_participants
      names = []
      emails = []
      for i in range(self.n_participants):
         names.append('Robot {}'.format(i))
         emails.append('robot_{}@skynet.gov'.format(i))
      self.participant_data['name'] = names
      self.participant_data['email'] = emails
      self.participant_info_read = True
      return
      
   def read_participant_data(self, filepath):
      """
      Read names and email addresses from a csv-file of participants
      """
      participant_data = pd.read_csv(filepath)
      self.n_participants = len(participant_data) 
      self.participant_data['name'] = participant_data['name']
      self.participant_data['email'] = participant_data['email']
      self.participant_info_read = True
      return
      
   ### Functions for creating account data
      
   def fill_in_data_fields(self):
      """
      Create account names and passwords for the participants, assuming a
      list of participants has been loaded or simulated.
      """
      if self.participant_info_read:
         IDs = self._generate_IDs()
         passwords = self._generate_passwords()
         self.account_data['user_id'] = IDs
         self.account_data['login_id'] = IDs
         self.account_data['password'] = passwords
         self.account_data['status'] = 'active'
         self.sharepoint_data['name'] = self.participant_data['name']
         self.sharepoint_data['email'] = self.participant_data['name']
         self.sharepoint_data['user_id'] = IDs
         self.sharepoint_data['password'] = passwords
      else:
         print("Cannot generate account data without participant data")
      return
      
   def _generate_IDs(self):
      IDs = []
      counter = 0
      total_possibilities = len(self.ID_generator.adjective_list) * len(self.ID_generator.noun_list)
      while len(IDs) < self.n_participants:
         if counter == total_possibilities:
            print("Ran out of possible IDs!")
            print("Word lists only permit {} combinations".format(total_possibilities))
            return IDs
         unadjusted = self.ID_generator.generate_ID()
         adjusted = unadjusted[0].upper() + unadjusted[1:].lower()
         if not (adjusted in IDs):
            IDs.append(adjusted)
         counter += 1
      return IDs
      
   def _generate_passwords(self):
      passwords = []
      for i in range(self.n_participants):
         passwords.append(self.password_generator.generate_password())
      return passwords
   
   def _hash_password(self, password, salt):
      hashed_password = hl.sha1('{}{}'.format(password,salt).encode(encoding='UTF-8'))
      digested_password = hashed_password.hexdigest()
      b64encoded_password = base64.b64encode(digested_password.encode() + salt.encode())
      return b64encoded_password.decode()
      
   ### Functions for saving data
   
   def save_participants(self, filepath):
      """
      Save data for the participants. In general, there is no reason to do
      this except for simulated data.
      """
      if self.participant_info_read:
         self.participant_data.to_csv(filepath, index=False)
      else:
         print("There is no data to save")
      return
   
   def save_account_IDs(self, filepath):
      """
      Save a list saying only which accounts exist, without connecting them
      to participants
      """
      IDs = self.account_data[['user_id']].sort_values('user_id')
      IDs.to_csv(filepath, index=False, header=False)
      return
   
   ### Functions for saving *sensitive* data
   ### NOTE: This information is in principle secret, meaning that is must
   ###       be stored in a place where it is accessible even to other
   ###       members of the project
   
   def save_account_data(self, filepath):
      """
      Save account data, with *unhashed* passwords, in a format that can be
      delivered to Canvas.
      
      NOTE: This must not be stored where it can be accessed by anyone except
            project members who have been authorised.
      """
      print(generic_warning)
      self.account_data.to_csv(filepath, index=False)
      return

   def save_account_data_hashed(self, filepath):
      """
      Save account data, with hashed passwords, in a format that can be
      delivered to Canvas
      
      The hashing procedure is described at:
      https://community.canvaslms.com/t5/SIS-User-Articles/SSHA-Password-Generation/ta-p/243730

      NOTE: This must not be stored where it can be accessed by anyone except
            project members who have been authorised.
      """
      print(generic_warning)
      hashed_passwords = []
      for password in self.account_data['password']:
         salt = ''.join(secrets.choice(string.ascii_letters) for i in range(16))
         hashed_passwords.append('{SSHA}' + self._hash_password(password, salt))
      hashed_data = self.account_data.drop('password', axis = 1)
      hashed_data['ssha_password'] = hashed_passwords
      hashed_data.to_csv(filepath, index=False)
      return
      
   def save_sharepoint_data(self, filepath):
      """
      Save the information that will be used by the sharepoint_robot
      module

      NOTE: This must not be stored where it can be accessed by anyone except
            project members who have been authorised.
      """
      print(generic_warning)
      self.sharepoint_data.to_csv(filepath, index=False)
      return
