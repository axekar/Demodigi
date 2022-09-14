'''
This module was written for the ESF-financed project Demokratisk
Digitalisering. The project is a collaboration between
Arbetsförmedlingen (AF) and Kungliga Tekniska Högskolan (KTH). The
purpose of the project is to increase the digital competence - as
defined at https://ec.europa.eu/jrc/en/digcomp - of people working at
Arbetsförmedlingen, and by extension also job seekers. This will be
done by learning modules at KTH using OLI-Torus.

--- About this Python module ---

This module is intended to do provide feedback to the participants in
our learning modules, using the Canvas API - which is documented at
https://canvas.instructure.com/doc/api/index.html - to send messages
to each participant.

Written by Alvin Gavel,
https://github.com/Alvin-Gavel/Demodigi
'''

import os

import requests as r

class UnexpectedResponseError(Exception):
    def __init__(self, msg):
        self.msg = msg
        return

def upload_file(file_path, user_id, token):
   """
   Upload a file to canvas
   """
   file_name = file_path.split('/')[-1]
   sz = os.stat(file_path).st_size
   payload = {
      'name': file_name,
      'size': sz,
   }
   header = {
      'Authorization': 'Bearer {}'.format(token)
   }
   
   response_1 = r.post('https://af.instructure.com/api/v1/users/{}/files'.format(user_id), data = payload, headers=header)
   if not 'OK' in response_1.headers['Status']:
      raise UnexpectedResponseError('When preparing for upload, canvas returned status "{}"'.format(response_1.headers['Status']))
   response_1_content = response_1.json()
   upload_url = response_1_content['upload_url']

   f = open(file_path, 'rb')
   response_2 = r.post(upload_url, files = {file_name: f})
   response_2_content = response_2.json()
   if not response_2_content['upload_status'] == 'success':
      raise UnexpectedResponseError('When uploading, canvas returned status "{}"'.format(response_2.headers['Status']))
   return
   
def send_file_contents(file_path, user_id, token):
   """
   Send the contents of a text file to a user
   """
   
   f = open(file_path, 'r')
   contents = f.read()
   f.close()
   
   payload = {
      'subject': 'Återkoppling på kartläggningsmodul',
      'force_new': True,
      'recipients': [user_id],
      'body': contents,
   }
   header = {
      'Authorization': 'Bearer {}'.format(token)
   }
   
   response = r.post('https://af.instructure.com/api/v1/conversations', data = payload, headers=header)
   response_content = response.json()
   if not type(response_content) == list:
      raise UnexpectedResponseError('When uploading, canvas returned error message "{}"'.format(response_content['errors'][0]['message']))
   return response


def account_name_user_id_mapping(token):
   """
   Canvas uses short user IDs that differ from the account names. This
   finds the mapping between the two.
   
   Note that this will include "users" like 'Outcomes Service API' and
   'Quizzes.Next Service API', so some filtering is necessary
   afterwards.
   """
   def find_next_link(link_long_string):
      """
      The get requests return a string which can be broken up into a comma-
      separated list, where each entry is a link to the first, current, next
      and previous (where a next and previous exist). This picks out which 
      one is the next.
      """
      link_strings = link_long_string.split(',')
      found = False
      for link_string in link_strings:
         if '; rel="next"' in link_string:
            link = link_string.split('>')[0].split('<')[1]
            found = True
            break
      if not found:
         link = None
      return link
   
   header = {
      'Authorization': 'Bearer {}'.format(token)
   }
   response = r.get('https://af.instructure.com/api/v1/accounts/1/users', headers=header)
   if not 'OK' in response.headers['Status']:
      raise UnexpectedResponseError('When accessing user list, canvas returned status "{}"'.format(response.headers['Status']))
      
   users = response.json()
      
   link = find_next_link(response.headers['Link'])
   while link != None:
      response = r.get(link, headers=header)
      users += response.json()
      link = find_next_link(response.headers['Link'])
   
   mapping = {}
   for user in users:
      mapping[user['name']] = user['id']
   return mapping
