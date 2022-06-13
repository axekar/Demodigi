"""
This module was written for the ESF-financed project Demokratisk
Digitalisering. The project is a collaboration between
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

 - It should be a Swedish word, not obscene or otherwise offensive

When generating passwords, I will take the following approach:

 - It should consist of five Swedish words, separated by spaces

 - It should consist of only lowercase letters. We will not do the
   mixing of cases, numbers and special characters that is typically
   recommended, since that makes passwords harder to remember without
   actually making them much more secure.

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
   to use them, or to allow quickly demonstrating why they are so bad.
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
      Optinal parameters:
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
      return self.delimiter.join(secrets.choice(self.alphabet) for i in range(self.length))
                   
   def print_info(self):
      """
      Gives some basic information about the method for generating passwords
      """
      print("The character list has {} entries".format(self.n_words))
      print("This permits about {:.0e} unique passwords, chosen with uniform probability".format(self.n_possible_passwords))
      print("This corresponds to {:.0f} bits of entropy".format(self.entropy))
      return


class participant_list:
   """
   This represents a list of people taking the learning module
   
   Attributes
   ----------
   [TBD]
   """
   def __init__(self, ID_wordlist, password_wordlist, password_length = 5):
      """
      Parameters
      ----------
      ID_wordlist : list of str
      \tDescribed under attributes
      password_wordlist : list of str
      \tDescribed under attributes

      Optional parameters
      -------------------
      password_length : int
      \tThe number of symbols that will make up a password
      """
      self.ID_wordlist = ID_wordlist
      self.password_wordlist = password_wordlist
      self.password_generator = password_generator(password_length, 'xkcd', wordlist = self.password_wordlist)
      self.participant_data = pd.DataFrame(columns = ['name', 'email', 'user_id'])
      self.account_data = pd.DataFrame(columns = ['user_id', 'login_id', 'password', 'status'])
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
      
   def generate_account_data(self):
      """
      Create account names and passwords for the participants, assuming a
      list of participants has been loaded or simulated.
      """
      if self.participant_info_read:
         IDs = self._generate_IDs()
         self.participant_data['user_id'] = IDs
         self.account_data['user_id'] = IDs
         self.account_data['login_id'] = IDs
         self.account_data['password'] = self._generate_passwords()
         self.account_data['status'] = 'active'
      else:
         print("Cannot generate account data without participant data")
      return
      
   def _generate_IDs(self):
      IDs = []
      for i in range(self.n_participants):
         unadjusted = secrets.choice(self.ID_wordlist)
         IDs.append(unadjusted[0].upper() + unadjusted[1:].lower())
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
   
   def save_account_data(self, filepath):
      """
      Save account data, with *unhashed* passwords
      """
      self.account_data.to_csv(filepath, index=False)
      return

   def save_account_data_hashed(self, filepath):
      """
      Save account data, with passwords hashed
      """
      hashed_passwords = []
      for password in self.account_data['password']:
         salt = ''.join(secrets.choice(string.ascii_letters) for i in range(16))
         hashed_passwords.append('{SSHA}' + self._hash_password(password, salt))
      hashed_data = self.account_data.drop('password', axis = 1)
      hashed_data['ssha_password'] = hashed_passwords
      hashed_data.to_csv(filepath, index=False)
      return
      
   def save_participant_data(self, filepath):
      """
      Save the names, emails and user_ids (if defined) for the particants
      """
      self.participant_data.to_csv(filepath, index=False)
      return
