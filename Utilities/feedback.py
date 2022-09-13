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


def upload(file_path, token):
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
   
   response_1 = r.post('https://af.instructure.com/api/v1/users/self/files', data = payload, headers=header)
   if not 'OK' in response_1.headers['Status']:
      print('Tried to prepare for upload')
      print('Got unexpected status in response from Canvas:')
      print(response_1.headers['Status'])
   response_1_content = response_1.json()
   upload_url = response_1_content['upload_url']

   f = open(file_path, 'rb')
   response_2 = r.post(upload_url, files = {file_name: f})
   response_2_content = response_2.json()
   if not response_2_content['upload_status'] == 'success':
      print('Tried to upload')
      print('Got unexpected status in response from Canvas:')
      print(response_2.headers['Status'])
   return
