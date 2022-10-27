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

import json
import pandas as pd
import base64
import hashlib as hl
   
# This module is secret, meaning it cannot be included in the repository.
from hash_username import hash_username

class HR_data:
   def __init__(self, salt, source_file_path, target_folder_path, manipulations = []):
      self.salt = salt
      self.source_file_path = source_file_path
      if target_folder_path[-1] != '/':
         target_folder_path += '/'
      self.target_folder_path = target_folder_path
      self.import_HR_data()
      self.make_usernames()
      self.manipulations = manipulations
      self.flags = self.flag_manipulations()
      self.versions = self.infer_version_names()
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
      self.usernames = np.asarray(IDs)
      self.n_users = len(self.usernames)
      self.mapping = pd.DataFrame(data={'user_id': IDs, '5-ställig kod':codes})
      self.mapping.to_csv('{}mapping.csv'.format(self.target_folder_path), index = False)
      return
   
   def infer_version_names(self):
      """
      Based on the n manipulations, come up with names for the 2^n versions
      of the learning modules that will need to exist on Canvas.
      """
      versions = set([])
      for i in range(self.n_users):
         flags = []
         for manipulation in self.manipulations:
            if self.flags[manipulation][i]:
               flags.append(manipulation)
         version = ", ".join(flags)
         if version == "":
            version = "default"
         if not (version in versions):
            versions.add(version)
      return versions
   
   def flag_manipulations(self):
      """
      Flag all participants according to a list of manipulations. This is
      done in a way that is in principle deterministic, but where there is
      no correlation between who the user is any what manipulations they get
      assigned to.
      """
      flags = {}
      for manipulation in self.manipulations:
         flags[manipulation] = []
      
      for code in self.HR['5-ställig kod'].values:
         for manipulation in self.manipulations:
            hashed = hl.sha1('{}{}'.format(code,manipulation).encode(encoding='UTF-8'))
            digested = hashed.digest()
            b64encoded = base64.b64encode(digested)
            flags[manipulation].append(b64encoded[0] % 2 == 0)
      for manipulation in self.manipulations:
         flags[manipulation] = np.asarray(flags[manipulation])
      return flags
         
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
      for ID in self.usernames:
         user_IDs.append(ID)
         login_IDs.append(ID)
         authentication_provider.append('openid_connect')
         first_name.append('Af'),
         last_name.append('Student')
         fake_emails.append('{}@arbetsformedlingen.se'.format(ID))
         status.append('active')
      self.SIS_data = pd.DataFrame(data={'user_id':user_IDs, 'login_id':login_IDs, 'authentication_provider_id':authentication_provider, 'first_name':first_name, 'last_name':last_name, 'email':fake_emails, 'status':status})
      return
   
   def export_SIS_data(self):
      self.SIS_data.to_csv('{}users.csv'.format(self.target_folder_path), index = False, encoding = 'utf-8')
      return
   
   def make_SIS_kickout_file(self, course_ID):
      """
      Given a list of five-character codes and a salt, this creates the basis
      for a SIS file which will kick them out from a course. This can come in
      handy, since the graphical user interface for Canvas does not have a
      bulk remove function, meaning that people have to be removed manually.
      Since we have in the order of thousands of users, this can be very
      tedious.
      """
      course_IDs = []
      user_IDs = []
      roles = []
      status = []
      for ID in self.usernames:
         course_IDs.append(course_ID)
         user_IDs.append(ID)
         roles.append('student')
         status.append('inactive')
      SIS_kickout = pd.DataFrame(data={'course_id': course_IDs, 'user_id':user_IDs, 'role':roles, 'status':status})
      SIS_kickout.to_csv('{}enrollments.csv'.format(self.target_folder_path), index = False, encoding = 'utf-8')
      return
   
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
   
   def export_manipulations(self):
      """
      Export a file of manipulation flags, which can be read by the
      module factorial_experiment
      """
      jsonable_manipulations = []
      jsonable_flags = {}
      for manipulation in self.manipulations:
         jsonable_manipulations.append(manipulation)
         jsonable_flags[manipulation] = self.flags[manipulation].tolist()
      f = open('{}Manipulations.json'.format(self.target_folder_path), 'w')
      packed = json.dumps({'IDs':self.SIS_data['user_id'].values.tolist(), 'Manipulations': jsonable_manipulations, 'Manipulation flags':jsonable_flags})
      f.write(packed)
      f.close()
      return

   def export_email_strings(self):
      """
      When adding users to courses, we need to cut&paste their pretend emails
      separated by commas
      """
      mail_lists = {}
      for version in self.versions:
         mail_lists[version] = []
      
      for i in range(self.n_users):
         mail = self.SIS_data['email'].values[i]
         ID = self.SIS_data['user_id'].values[i]
         flags = []
         for manipulation in self.manipulations:
            if self.flags[manipulation][i]:
               flags.append(manipulation)
         version = ", ".join(flags)
         if version == '':
            version = 'default'
         mail_lists[version].append(mail)          # Changed to mail (from ID), since this is to be to add user emails /axekar
         
      len_mail_list = 0
      for version in self.versions:
         len_mail_list = max(len_mail_list, len(mail_lists[version]))
      
      n_per_chunk = 500
      n_chunks = len_mail_list // n_per_chunk + 1
      
      for version in self.versions:
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
      fake_mails = {}
      for version in self.versions:
         fake_mails[version] = []
      
      for mail in mails:
         mail = mail.strip()
         try:
            index = (self.HR['e-post'] == mail)
            ID = self.usernames[index][0]
            
            flags = []
            for manipulation in self.manipulations:
               if self.flags[manipulation][index]:
                  flags.append(manipulation)
            version = ", ".join(flags)
            if version == '':
               version = 'default'
            
            fake_mails[version].append('{}@arbetsformedlingen.se'.format(ID))
         except IndexError:
            print('No match for {}'.format(mail))
           
      mail_strings = {} 
      for version in self.versions:
         mail_strings[version] = ', '.join(fake_mails[version])
      return mail_strings
   
   def generate_data(self, manipulations = ['']):
      """
      Generate all of the data that different people in the project are likely
      to need.
      """
      self.make_SIS_data()
      self.export_SIS_data()
      self.mail_by_region()
      self.export_manipulations()
      self.export_bureaucracy()
      self.export_email_strings()
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
      file contains one sheet of data to be delivered directly to SCB. It
      also has one sheet per department which contains email addresses, and
      can be used to send reminders for people who are late with doing the
      course.
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
