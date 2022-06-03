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

 - It should consist of five Swedish word, separated by spaces

 - It should consist of only lowercase letters. We will not do the
   mixing of cases, numbers and special characters that is typically
   recommended, since that makes passwords harder to remember without
   actually making them much more secure.

Written by Alvin Gavel,

https://github.com/Alvin-Gavel/Demodigi
"""

import secrets

class wordlist:
   """
   This is a list of words used when generating account IDs and
   passwords. This will work if you are working on Ubuntu. If you are
   a Windows user, feel free to adapt the code to get it to work for
   you.

   Attributes
   ----------
   words : list of str
   \tThe words that will be used to generate IDs and passwords
   """
   def __init__(self, language):
      """
      Parameters
      ----------
      language : str
      \tTells the wordlist which dict file to choose
      """
      if language.lower() == 'english':
         fpath = '/usr/share/dict/words'
      else:
         print('Cannot recognise language {}'.format(language))
         return
      f = open(fpath)
      self.words = [word.strip() for word in f]
      f.close()
      return


class participant:
   """
   This represents a single person taking a learning module.
   
   Attributes
   ----------
   ID : string
   \tSome unique identifier of the participant. This will be a noun in
   \tthe Swedish language.
   password : string
   \tAn easy-to-remember but hard-to-guess passphrase necessary for
   \tlogging in on our learning platform. It will be a sequence of five
   \twords in the Swedish language.
   """
   def __init__(self, wordlist):
      """
      Parameters
      ----------
      wordlist : wordlist object
      \tAn object containing the words to generate IDs and passwords from
      """
      self.wordlist = wordlist
      self.ID = self.generate_ID()
      self.password = self.generate_password()
      return
      
   def generate_ID(self):
      return secrets.choice(self.wordlist.words)
      
   def generate_password(self):
      return ' '.join(secrets.choice(self.wordlist.words) for i in range(5))
   
