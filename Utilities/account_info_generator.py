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
   def __init__(self):
      self.ID = self.generate_ID()
      self.password = self.generate_password()
      return
      
   def generate_ID(self):
      with open('/usr/share/dict/words') as f:
         words = [word.strip() for word in f]
      return secrets.choice(words)
      
   def generate_password(self):
      with open('/usr/share/dict/words') as f:
         words = [word.strip() for word in f]
      return ' '.join(secrets.choice(words) for i in range(5))
   
