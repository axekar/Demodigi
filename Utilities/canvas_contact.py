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
from datetime import datetime

import requests as r
import pandas as pd
import tqdm

import extra_functions as ef

class UnexpectedResponseError(Exception):
    def __init__(self, msg):
        self.msg = msg
        return

def account_name_user_id_mapping(token, verbose = False):
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
      n_read = len(users)
      if verbose and n_read % 100 == 0:
         print('Read {} users so far'.format(n_read))
   
   mapping = {}
   for user in users:
      try:
         mapping[user['login_id']] = user['id']
      except KeyError:
         pass
   return mapping


def send_file_contents(file_path, user_id, subject, token):
   """
   Send a message to a participant, with the message text taken from a
   file.
   """
   f = open(file_path, 'r')
   contents = f.read()
   f.close()
   
   payload = {
      'subject': subject,
      'force_new': True,
      'recipients': [user_id],
      'body': contents,
      'group_conversation':False
   }
   header = {
      'Authorization': 'Bearer {}'.format(token)
   }
   
   response = r.post('https://af.instructure.com/api/v1/conversations', data = payload, headers=header)
   response_content = response.json()
   if not type(response_content) == list:
      raise UnexpectedResponseError('When uploading, canvas returned error message "{}"'.format(response_content['errors'][0]['message']))
   return


def upload_file(file_path, canvas_path, user_id, token):
   """
   Upload a file to a particular path, in the Canvas API, while acting as
   a specific user - possibly yourself.
   """
   header = {
      'Authorization': 'Bearer {}'.format(token)
   }

   file_name = file_path.split('/')[-1]
   sz = os.stat(file_path).st_size
   payload = {
      'name': file_name,
      'size': sz,
      'as_user_id': user_id
   }

   response_1 = r.post(canvas_path, data = payload, headers=header)
   if not 'OK' in response_1.headers['Status']:
      raise UnexpectedResponseError('When preparing for upload, canvas returned status "{}"'.format(response_1.headers['Status']))
   response_1_content = response_1.json()
   upload_url = response_1_content['upload_url']

   f = open(file_path, 'rb')
   response_2 = r.post(upload_url, files = {file_name: f})
   response_2_content = response_2.json()
   if not response_2_content['upload_status'] == 'success':
      raise UnexpectedResponseError('When uploading, canvas returned status "{}"'.format(response_2.headers['Status']))
   return response_2_content['id']


def upload_conversation_attachment(file_path, user_id, token):
   """
   Upload a conversation attachment to user file area. Typically, this
   would be your own, in preparation for sending a message to another
   user with that file attached.
   """
   header = {
      'Authorization': 'Bearer {}'.format(token)
   }
   
   response_1 = r.get('https://af.instructure.com/api/v1/users/{}/folders'.format(user_id), headers = {'Authorization': 'Bearer {}'.format(token)})
   if not 'OK' in response_1.headers['Status']:
      raise UnexpectedResponseError('When locating conversation attachment folder, canvas returned status "{}"'.format(response_1.headers['Status']))
   response_1_content = response_1.json()
   
   found = False
   for item in response_1_content:
      if item['full_name'] == 'my files/conversation attachments':
         found = True
         folder_id = item['id']
         break
   if not found:
      raise UnexpectedResponseError("Could not locate 'conversation attachments' folder")
   
   file_id = upload_file(file_path, 'https://af.instructure.com/api/v1/folders/{}/files'.format(folder_id), user_id, token)
   return file_id


def send_file(file_path, self_id, target_id, subject, message, token):
   """
   Send a message to a participant, containing an attached file.
   """
   file_id = upload_conversation_attachment(file_path, self_id, token)
   
   payload = {
      'subject': subject,
      'force_new': True,
      'recipients': [target_id],
      'attachment_ids[]':[file_id],
      'body': message,
      'mode':'sync'
   }
   header = {
      'Authorization': 'Bearer {}'.format(token)
   }

   response = r.post('https://af.instructure.com/api/v1/conversations', data = payload, headers=header)
   response_content = response.json()
   if not type(response_content) == list:
      raise UnexpectedResponseError('When uploading, canvas returned error message "{}"'.format(response_content['errors'][0]['message']))
   return

def read_account_names(filepath):
   """
   Reads a list of the participants' account names.
   """
   file_ending = filepath.split('.')[-1]
   if file_ending == 'txt':
      f = open(filepath)
      # I don't think this replacement is necessary any more.
      IDs = [word.strip().replace('@arbetsformedlingen.se', '') for word in f]
      f.close()
   elif file_ending == 'xlsx':
      dataframe = pd.read_excel(filepath, header = 0, dtype = str)
      IDs = list(dataframe['user_id'])
   else:
      print('Cannot recognise file type of {}'.format(filepath))
   return IDs

def send_feedback(account_name_path, feedback_folder_path, self_account, subject, message, token, verbose = False, test = False):
   """
   Take a list of participants and a folder of feedback created by the
   preprocessing module and deliver feedback to those who have not yet
   received feedback.
   """
   def update_trackers(already_received_feedback, received_feedback_now, daily_tracker_file_path, total_tracker_file_path, tracker_memory_file_path):
      f = open(daily_tracker_file_path, 'w')
      f.write('\n'.join(received_feedback_now))
      f.close()
   
      # Save a file with all the people who have ever received feedback
      have_received_feedback = already_received_feedback + received_feedback_now
      f = open(total_tracker_file_path, 'w')
      f.write('\n'.join(have_received_feedback))
      f.close()

      f = open(tracker_memory_file_path, 'w')
      f.write('\n'.join(have_received_feedback))
      f.close()
      return
      
   
   if feedback_folder_path[-1] != '/':
      feedback_folder_path += '/'
      
   # This will keep track of which participants have already received feedback
   tracker_folder_path = '{}Tracker/'.format(feedback_folder_path)
   daily_tracker_folder_path = '{}Daily_deliveries/'.format(tracker_folder_path)
   total_tracker_folder_path = '{}Total_delivered/'.format(tracker_folder_path)

   ef.make_folder(tracker_folder_path)
   ef.make_folder(daily_tracker_folder_path)
   ef.make_folder(total_tracker_folder_path)
   
   total_tracker_file_path = '{}Current.txt'.format(total_tracker_folder_path)
   if not os.path.isfile(total_tracker_file_path):
      f = open(total_tracker_file_path, 'w')
      f.close()
   
   f = open(total_tracker_file_path, 'r')
   already_received_feedback = [ID.strip() for ID in f]
   f.close()
   
   accounts = read_account_names(account_name_path)
   mapping = account_name_user_id_mapping(token, verbose = verbose)
   n_sent = 0
   received_feedback_now = []

   # Define paths to files of trackers
   today = datetime.today().strftime('%Y-%m-%d')
   daily_tracker_file_path = '{}{}.txt'.format(daily_tracker_folder_path, today)
   i = 1
   while os.path.isfile(daily_tracker_file_path):
      daily_tracker_file_path = '{}{}_{}.txt'.format(daily_tracker_folder_path, today, i)
      i += 1

   tracker_memory_file_path = '{}{}.txt'.format(total_tracker_folder_path, today)
   i = 1
   while os.path.isfile(tracker_memory_file_path):
      tracker_memory_file_path = '{}{}_{}.txt'.format(total_tracker_folder_path, today, i)
      i += 1
   
   if verbose:
      print("Delivering participants' feedback. This may take a while...")
   for target_account in tqdm.tqdm(accounts):
      file_path = '{0}{1}/Återkoppling_deltagare_{1}.docx'.format(feedback_folder_path, target_account.replace('/', '_'))
      if os.path.isfile(file_path):
         if target_account in already_received_feedback:
            pass
         else:
            try:
               if not test:
                  send_file(file_path, mapping[self_account], mapping[target_account], subject, message, token)
                  received_feedback_now.append(target_account)
                  if n_sent % 100 == 0:
                     update_trackers(already_received_feedback, received_feedback_now, daily_tracker_file_path, total_tracker_file_path, tracker_memory_file_path)
               n_sent += 1
            except KeyError:
               print('Could not find mapping for account {}'.format(target_account))
   print('There were {} participants in ID file'.format(len(accounts)))
   print('There were {} already tagged as having received feedback'.format(len(already_received_feedback)))
   if not test:
      print('Delivered {} files of feedback'.format(n_sent))
   else:
      print('Would have delivered {} files of feedback'.format(n_sent))

   update_trackers(already_received_feedback, received_feedback_now, daily_tracker_file_path, total_tracker_file_path, tracker_memory_file_path)

   return
