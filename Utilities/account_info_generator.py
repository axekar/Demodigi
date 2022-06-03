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

import sys
import secrets

import pandas as pd

class wordlist:
   """
   This is a list of words used when generating account IDs and
   passwords.

   Attributes
   ----------
   words : list of str
   \tThe words that will be used to generate IDs and passwords
   n_words : int
   \tThe number of words in the word list
   n_passwords : int
   \tThe number of unique five-word passwords that can be generated using
   \tthis word list
   """
   def __init__(self, language):
      """
      Parameters
      ----------
      language : str
      \tTells the wordlist which dict file to choose
      """
      self.words = self.try_automatic_reading(language)
      self.n_words = len(self.words)
      self.n_passwords = self.n_words**5
      return
      
   def try_automatic_reading(self, language):
      if sys.platform in ["linux", "linux2"]:
         if language.lower() == 'english':
            fpath = '/usr/share/dict/words'
         elif language.lower() == 'swedish':
            fpath = '/usr/share/dict/svenska'
         else:
            print('Cannot recognise language {}'.format(language))
            return []
      else:
         print('You will have to supply a dictionary file manually')
         return []
      words = self.read_dictionary_file(fpath)
      return words
                   
   def read_dictionary_file(self, fpath):
      """
      Read a dictionary file containing one word per line
      """
      f = open(fpath, encoding='latin-1')
      words = [word.strip() for word in f]
      f.close()
      return words
      
   def print_info(self):
      print("This word list has {} entries".format(self.n_words))
      print("This permits about {:.0e} unique passwords".format(self.n_passwords))

class participant_list:
   """
   This represents a list of people taking the learning module
   
   Attributes
   ----------
   n_participants : int
   \tThe number of participants in the learning module
   wordlist : wordlist object
   \tAn object containing the words to generate IDs and passwords from
   account_data : pandas DataFrame
   \tThe IDs and passwords of the participants
   """
   def __init__(self, n_participants, wordlist):
      """
      Parameters
      ----------
      n_participants : int
      \tDescribed under attributes
      wordlist : wordlist object
      \tDescribed under attributes
      """
      self.n_participants = n_participants
      self.wordlist = wordlist
      self.account_data = pd.DataFrame()
      self.account_data['ID'] = self.generate_IDs()
      self.account_data['password'] = self.generate_passwords()
      return
      
   def generate_IDs(self):
      IDs = []
      for i in range(self.n_participants):
         unadjusted = secrets.choice(self.wordlist.words)
         IDs.append(unadjusted[0].upper() + unadjusted[1:].lower())
      return IDs
      
   def generate_passwords(self):
      passwords = []
      for i in range(self.n_participants):
         passwords.append(' '.join(secrets.choice(self.wordlist.words) for i in range(5)).lower())
      return passwords
   
   def save_data(self, filepath):
      """
      Unfortunately, it seems that we will supply the IDs and passwords to
      the learning platform in the form of a csv-file where the passwords
      are written in plaintext. Needless to say, I take no responsibility
      for any consequences of doing this.
      """
      self.account_data.to_csv(filepath, index=False)
      return
   
      
