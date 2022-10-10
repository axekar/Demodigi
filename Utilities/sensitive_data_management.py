"""
This module was written for the ESF-financed project Demokratisk
Digitalisering. The project is a collaboration between
Arbetsförmedlingen (AF) and Kungliga Tekniska Högskolan (KTH). The
purpose of the project is to increase the digital competence - as
defined at https://ec.europa.eu/jrc/en/digcomp - of people working at
Arbetsförmedlingen, and by extension also job seekers. This will be
done by learning modules at KTH using OLI-Torus.

--- About this Python module ---

This module is intended to handle data which is sensitive for various
reasons, such as the list of AF employees given to us by the HR
department. It uses a hash function which is considered to be secret,
and therefore is not included in the repository.

Written by Alvin Gavel,
https://github.com/Alvin-Gavel/Demodigi
"""

import os
import numpy as np

import pandas as pd
   
# This module is secret, meaning it cannot be included in the repository.
from hash_username import hash_username

class HR_data:
   def __init__(self, salt, source_file_path, target_folder_path):
      self.salt = salt
      self.source_file_path = source_file_path
      if target_folder_path[-1] != '/':
         target_folder_path += '/'
      self.target_folder_path = target_folder_path
      self.import_HR_data()
      return
      
   def make_usernames(self):
      """
      Make usernames based on the five-character codes, and save the mapping
      in three formats for ease of access.
      """
      self.mapping_code_username = {}
      self.mapping_username_code = {}

      codes = list(self.HR['5-ställig kod'])
      IDs = []
      for code in codes:
         ID = hash_username(code, self.salt).decode()
         IDs.append(ID)
         self.mapping_code_username[code] = ID
         self.mapping_username_code[ID] = code
      self.mapping = pd.DataFrame(data={'user_id': IDs, '5-ställig kod':codes})
      self.mapping.to_csv('{}mapping.csv'.format(self.target_folder_path), index = False)
      return
         
   def import_HR_data(self, verbose = True):
      """
      Import a list of employees, following the format of the file given to
      us by the HR department.
      """
      if verbose:
         print("Reading HR file")
      HR = pd.read_excel(self.source_file_path, names = ['5-ställig kod', 'Personnr', 'Efternamn', 'Förnamn', 'Orgnr', 'Orgenhet', 'e-post', 'konsult', 'VO', 'Region'], dtype = str)
      full_length = len(HR.index)
      if verbose:
         print("Read {} in total".format(full_length))
      HR = HR[HR['konsult'] != 'Ja']
      length = len(HR.index)
      if verbose:
         print("Of these, {} remain after dropping consults".format(length))
         
      # For some reason the lists we get from the HR department have a lot
      # of trailing whitespace
      for key in HR.keys():
         HR[key] = HR[key].str.strip()
      self.HR = HR
      self.make_usernames()
      return

   def make_SIS_data(self):
      """
      Given a list of five-character codes and a salt, use them to generate
      the account names used by SSO.
      """
      user_IDs = []
      login_IDs = []
      authentication_provider = []
      first_name = []
      last_name = []
      fake_emails = []
      status = []
      for ID in self.mapping['user_id']:
         user_IDs.append(ID)
         login_IDs.append(ID)
         authentication_provider.append('openid_connect')
         first_name.append('Af'),
         last_name.append('Student')
         fake_emails.append('{}@arbetsformedlingen.se'.format(ID))
         status.append('active')
      SIS_data = pd.DataFrame(data={'user_id':user_IDs, 'login_id':login_IDs, 'authentication_provider_id':authentication_provider, 'first_name':first_name, 'last_name':last_name, 'email':fake_emails, 'status':status})
      return SIS_data
    
   def mail_by_region(self):
      """
      Make lists of email adresses per region.
      """
      regions = set(self.HR['Region'])
      regions.discard(np.nan)
      with pd.ExcelWriter('{}Mail_per_region.xlsx'.format(self.target_folder_path)) as f:
         for region in regions:
            correct_region = self.HR[self.HR['Region'] == region]
            correct_region['e-post'].to_excel(f, index = False, sheet_name = region)
      return
    
   def export_bureaucracy(self):
      """
      For bureaucratic reasons, we need to deliver one file of first names,
      one file of lastnames and also a file of user IDs.
      """
      self.SIS_data['user_id'].to_excel('{}Användarnamn.xlsx'.format(self.target_folder_path), index=False)
      self.HR['Förnamn'].to_excel('{}Förnamn.xlsx'.format(self.target_folder_path), index=False)
      self.HR['Efternamn'].to_excel('{}Efternamn.xlsx'.format(self.target_folder_path), index=False)
      return
   
   def export_email_strings(self, module_versions = ['default']):
      """
      When adding users to courses, we need to cut&paste their pretend emails
      separated by commas
      """
      mail_lists = {}
      for version in module_versions:
         mail_lists[version] = []
      
      for mail, ID in zip(self.SIS_data['email'].values, self.SIS_data['user_id']):
         version = module_versions[ord(ID[0]) % len(module_versions)]
         mail_lists[version].append(ID)
         
      len_mail_list = 0
      for version in module_versions:
         len_mail_list = max(len_mail_list, len(mail_lists[version]))
      
      n_per_chunk = 500
      n_chunks = len_mail_list // n_per_chunk + 1
      
      for version in module_versions:
         mail_list = mail_lists[version]
         chunks = np.array_split(mail_list, n_chunks)
         
         for i in range(n_chunks):
            chunk = chunks[i]
            mail_string = ', '.join(chunk)
            f = open('{}email_string_{}_{}.txt'.format(self.target_folder_path, version, i), 'w')
            f.write(mail_string)
            f.close()
      return
   
   def transform_real_email_to_fake(self, mailstring):
      """
      This is intended to deal with the specific situation where people contact us
      with their work email and report that they cannot access a course on Canvas.
      In that case, we want to get a string with the face email addresses used on
      Canvas as their ideas, so that they can be cut&pasted into the Canvas
      interface.
      """
      mails = mailstring.split(',')
      IDs = []
      for mail in mails:
         mail = mail.strip()
         try:
            code = self.HR['5-ställig kod'][self.HR['e-post'] == mail].values[0]
            IDs.append(hash_username(code, self.salt).decode() + '@arbetsformedlingen.se')
         except IndexError:
            print('No match for {}'.format(mail))
      return ', '.join(IDs)
   
   def generate_data(self, module_versions = ['default']):
      """
      Generate all of the data that different people in the project are likely
      to need.
      """
      self.SIS_data = self.make_SIS_data()
      self.SIS_data.to_csv('{}users.csv'.format(self.target_folder_path), index = False, encoding = 'utf-8')
      self.mail_by_region()
      self.export_bureaucracy()
      self.export_email_strings(module_versions = module_versions)
      return
      
   def emails_from_participant_list(self, source_file_path):
      """
      Given a list containing a single column participant IDs, this creates
      a file with a single column of their email adresses, assuming that they
      can be found in the file of HR data. 
      """
      f = open(source_file_path)
      IDs = [word.strip() for word in f]
      f.close()
      emails = []
      for ID in IDs:
         try:
            # This is almost certainly not the correct way of doing this, but it works
            email = list(self.HR['e-post'][self.HR['5-ställig kod'] == self.mapping_username_code[ID.replace('@arbetsformedlingen.se', '')]])[0]
            emails.append(email)
         except KeyError:
            print('Could not find mail for user id {}'.format(ID))
      mail_pd = pd.DataFrame(data={'email':emails})
      mail_pd.to_csv('{}emails.txt'.format(self.target_folder_path), index = False)
      return
      
   def convert_SCB_data(self, source_file_path, target_file_path):
      """
      Take a preliminary SCB file and transform it into a final file. This
      file contains one sheet of 
      """
      SCB_prelim = pd.read_csv(source_file_path, names = ['Användarnamn', 'Uppskattad tid', 'Startdatum', 'Avslutsdatum'], dtype = str, skiprows = [0])
      
      person_numbers = []
      emails = []
      regions = []
      for ID in SCB_prelim['Användarnamn']:
         try:
            correct_person = self.HR['5-ställig kod'] == self.mapping_username_code[ID.replace('@arbetsformedlingen.se', '')]
            person_number = list(self.HR['Personnr'][correct_person])[0]
            if len(person_number) == 10:
               person_number = person_number[:6] + '-' + person_number[6:]
            elif len(person_number) == 12:
               person_number = person_number[:8] + '-' + person_number[8:]
            else:
               print('Person number {} does not match expected format'.format(person_number))
            person_numbers.append(person_number)
            emails.append(list(self.HR['e-post'][correct_person])[0])
            
            region = list(self.HR['Region'][correct_person])[0]
            regions.append(region)
         except KeyError:
            print('Could not find person number for user id {}'.format(ID))
            person_numbers.append('Ej känt')
            emails.append('Ej känd')
            regions.append('Ej känd')      
      SCB_first_page = SCB_prelim[['Uppskattad tid', 'Startdatum', 'Avslutsdatum']].copy()
      SCB_first_page.insert(0, 'Personnummer', person_numbers)
      
      SCB_following_pages = SCB_prelim[['Startdatum', 'Avslutsdatum']].copy()
      SCB_following_pages['e-post'] = emails
      SCB_following_pages['Region'] = regions
      
      all_regions = set(regions)
      all_regions.discard(np.nan)
      
      with pd.ExcelWriter(target_file_path) as f:
         SCB_first_page.to_excel(f, index = False, sheet_name = 'Samtliga')
         
         for region in sorted(list(all_regions)):
            correct_region = SCB_following_pages['Region'] == region
            SCB_following_pages[correct_region].to_excel(f, index = False, sheet_name = region)
      return
