"""
This module was written for the ESF-financed project Demokratisk
Digitalisering. The project is a collaboration between
Arbetsförmedlingen (AF) and Kungliga Tekniska Högskolan (KTH). The
purpose of the project is to increase the digital competence - as
defined at https://ec.europa.eu/jrc/en/digcomp - of people working at
Arbetsförmedlingen and by extension also job seekers. This will be
done by learning modules at KTH using OLI-Torus.

--- About this Python module ---

In the project, we will have to send the participants the names and
passwords of their accounts on our learning platform - which is likely
to be Canvas. For reasons of security, we do not want to simply mail
them the passwords in plaintext. One possible way of doing this - which
this module is intended to test - is to create a SharePoint page that
contains one list for each participant, which in turn contains the
account name and password. Each list should be accessible only to that
participant, meaning that it should be connected to their AF account.

Since the project will have around 8000-11000 participants, we do not
want to create these lists manually. Unfortunately, we do not have any
automatic way of creating pages in SharePoint. Hence, our solution is
to use Selenium to implement a "robot" that creates the SharePoint
lists.

In addition to the passwords, we also want to deliver feedback to the
participants. It is not yet fully defined what that feedback will look
like, but this module contains a skeleton of functions for doing that.

--- About getting the module to run

Running the module currently requires Chrome/Chromium, although it is
probably trivial to modify it to use Firefox. By default the module
assumes that the drivers are stored in a directory named "Drivers".

NOTE: If you are on Windows, running this code with a script, and
running the exact same instructions interactively in Ipython, is not
guaranteed to give identical results. In some cases, using a script
will cause a crash as letters with umlauts end up being garbled.


Written by Alvin Gavel,
https://github.com/Alvin-Gavel/Demodigi
"""

import selenium as sl
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

import numpy as np
import csv
from datetime import datetime
from time import sleep


class participant():
   def __init__(self, name, code):
      self.name = name
      self.code = code
      return


class participant_info(participant):
   """
   A person who participates in a learning module, to whom we want to
   deliver Canvas account information.
   
   Attributes
   ----------
   name : str
   \tName of the particpant
   \tused at AF
   code : str
   \t5-character code used internally within AF
   username : str
   \tName of Canvas account
   password : str
   \tPassword to Canvas account
   """
   def __init__(self, name, code, username, password):
      participant.__init__(self, name, code)
      self.username = username
      self.password = password
      return


class participant_feedback(participant):
   """
   A person who has participated in a learning module, to whom we want to
   deliver feedback on how well they did
   
   Attributes
   ----------
   name : str
   \tName of the particpant
   code : str
   \t5-character code internally within AF
   feedback_text : str
   \tThe feedback that we want to deliver. NB: This is preliminary, we will
   \tmost likely instead have a list of flags for which of a number of text
   \ttemplates to use.
   """
   def __init__(self, name, code, feedback_text):
      participant.__init__(self, name, code)
      self.feedback_text = feedback_text
      return


class clicker:
   """
   A device that reads lists of our participants and writes information to
   a SharePoint page.
   
   Attributes
   ----------
   connection : SharepointConnection
   \tThe connection used to communicate with the SharePoint page
   participants : list of participant
   \tThe participants that Canvas account information should be delivered to
   real_data : bool
   \tWhether the data represents actual people or simulated participants
   """

   def __init__(self, connection):
      self.connection = connection
      self.participants = []
      self.real_data = False
      return


class password_clicker(clicker):
   """
   A device for writing passwords to a SharePoint page
   """
   def __init__(self, connection):
      clicker.__init__(self, connection)
      return
   
   def read_participant_list(self, path):
      """
      Reads a csv-file of participants, in the format
      name, code, username, password
      """
      f = open(path, 'r', newline='', encoding='utf-8')
      reader = csv.reader(f, delimiter = ',')
      # Skip header
      next(reader)
      self.participants = []
      for line in reader:
         name = line[0].strip()
         code = line[1].strip()
         username = line[2].strip()
         password = line[3].strip()
         self.participants.append(participant_info(name, code, username, password))
      f.close()
      
      self.real_data = True
      return
   
   def simulate_participant_list(self, n_participants):
      """
      Generate a list of pretended particpants
      """
      self.participants = []
      for i in range(n_participants):
         self.participants.append(participant_info('Robot {}'.format(i), 'rbt{}'.format(i), 'usr{}'.format(i), '123456'))
      self.real_data = False
      return
   
   def construct_sharepoint_lists(self):
      """
      Construct lists on SharePoint which contain the username and password
      for each participant, and makes that information available to that
      participant and noone else.
      """
      self.connection.start_driver()
      for participant in self.participants:
         self.connection.make_id_pwd_list(participant, self.real_data)
      self.connection.stop_driver()
      return
      
   def verify_sharepoint_lists(self):
      """
      Verify that participants have correctly been written to SharePoint
      """
      self.connection.start_driver()
      correct = []
      for participant in self.participants:
         correct.append(self.connection.check_id_pwd_list(participant))
      self.connection.stop_driver()
      if sum(correct) == 0:
         for participant, correctness in zip(self.participants, correct):
            if not correctness:
               print('Problems with list for {}'.format(participant.name))
      else:
         print('All participants seem to have correct lists')
      return


class feedback_clicker(clicker):
   """
   A device for writing feedback to a SharePoint page
   """
   def __init__(self, connection):
      clicker.__init__(self, connection)
      return

   def simulate_participant_list(self, n_participants):
      """
      Generate a list of pretended particpants
      """
      self.participants = []
      for i in range(n_participants):
         self.participants.append(participant_feedback('Robot {}'.format(i), 'rob{}@skynet.com'.format(i), 'Bra jobbat!'))
      self.real_data = False
      return

   def deliver_feedback(self):
      """
      Construct pages on SharePoint which contain feedback for each
      participant.
      """
      self.connection.start_driver()
      for participant in self.participants:
         self.connection.deliver_feedback(participant, self.real_data)
      self.connection.stop_driver()
      return
      
class SharePointConnection(object):
   """
   Used for communicating with SharePoint
   
   Attributes
   ----------
   start_page_path : str
   \Web address of the SharePoint page
   start_page_name : str
   \tName of the SharePoint page. Used for granting and removing
   \tpermissions.
   browser : str
   \tThe browser to be used. So far the only choice sure to work is Chrome
   driver_directory_path : str
   \tPath to the directory where the drivers are kept
   """
   def __init__(self, start_page_path, start_page_name, browser, driver_directory_path):
      self.start_page_path = start_page_path
      self.start_page_name = start_page_name
      self.browser = browser
      self.driver_directory_path = driver_directory_path
      self.session_start_time = datetime.now()
      self.driver = None
      return
      
   def start_driver(self):
      print('Starting driver...')
      if self.browser == 'Chrome':
         chrome_options = sl.webdriver.chrome.options.Options()
         chrome_options.add_argument("--disable-extensions")
         chrome_options.add_argument("--start-maximized")        
         self.driver = sl.webdriver.Chrome(chrome_options = chrome_options, executable_path = self.driver_directory_path + '/chromedriver')
      elif self.browser == 'Firefox':
         firefox_options = sl.webdriver.firefox.options.Options()
         self.driver = sl.webdriver.Firefox(executable_path = self.driver_directory_path + '/geckodriver')
      else:
         print('Cannot find browser option!')
         self.driver = None
      print('Started driver!')
      self.session_start_time = datetime.now()
      return

   def stop_driver(self):
      self.driver.quit()
      return

   def go_to_page(self, adress):
      self.driver.get(adress)
      return
      
   def go_to_start(self):
      self.go_to_page(self.start_page_path)
      return

   def add_participant_as_member(self, participant, real_data):
      settings_menu = self.driver.find_element(By.CSS_SELECTOR, "[aria-label='Open the Settings menu to access personal and app settings']")
      settings_menu.click()
      sleep(2)
      settings_button = self.driver.find_element(By.CSS_SELECTOR, "[aria-label='Site permissions']")
      settings_button.click()
      sleep(5)
      share_button = self.driver.find_element(By.XPATH, "//*[text()='Share site']")
      share_button.click()
      sleep(2)
      add_field = self.driver.find_element(By.CSS_SELECTOR, "[aria-label='Add members to the site']")
      add_field.click()
      if not real_data:
         address = 'alvin.gavel@arbetsförmedlingen.se'
      else:
         address = participant.code
      add_field.send_keys(address)
      sleep(2)
      add_field.send_keys(Keys.RETURN)
      sleep(2)
      add_button = self.driver.find_element(By.XPATH, "//*[text()='Add']")
      add_button.click()
      sleep(2)
      return
      
   def create_list(self, description, participant):
      self.go_to_start()
      sleep(20)
      new_button = self.driver.find_element(By.NAME, "New")
      new_button.click()
      sleep(2)
      list_choice = self.driver.find_element(By.NAME, "List")
      list_choice.click()
      sleep(2)
      name_field = self.driver.find_element(By.XPATH, "//*[text()='Name']/following::input[@type='text']")
      name_field.send_keys("{}".format(participant.name))
      sleep(2)
      desc_field = self.driver.find_element(By.XPATH, "//*[text()='Description']/following::textarea")
      desc_field.send_keys(description)
      sleep(2)
      create_button = self.driver.find_element(By.CSS_SELECTOR, "[aria-label=Create]")
      create_button.click()
      sleep(20)
      return
      
   def set_read_privileges(self, participant, real_data):
      """
      This sets the read privileges for a list of a SharePoint page.
      Unfortunately, this is much less trivial to do for anything other than
      lists. Hence, we implement feedback as a list even though this is not
      the most obvious choice of format.
      """
      settings_menu = self.driver.find_element(By.CSS_SELECTOR, "[aria-label='Open the Settings menu to access personal and app settings']")
      settings_menu.click()
      sleep(2)
      settings_button = self.driver.find_element(By.CSS_SELECTOR, "[aria-label='List settings']")
      settings_button.click()
      sleep(5)
      permissions_link = self.driver.find_element(By.XPATH, "//*[text()='Permissions for this list']")
      permissions_link.click()
      sleep(5)
      stopinherit_button = self.driver.find_element(By.ID, "Ribbon.Permission.Manage.StopInherit-Large")
      stopinherit_button.click()
      sleep(2)
      self.driver.switch_to.alert.accept()
      sleep(2)
      visitor_checkbox = self.driver.find_element(By.XPATH, "//*[@title='Besökare på {}']".format(self.start_page_name))
      visitor_checkbox.click()
      removeperm_button = self.driver.find_element(By.ID, "Ribbon.Permission.Modify.RemovePerms-Large")
      removeperm_button.click()
      self.driver.switch_to.alert.accept()
      sleep(5)
      member_checkbox = self.driver.find_element(By.XPATH, "//*[@title='Medlemmar på {}']".format(self.start_page_name))
      member_checkbox.click()
      removeperm_button = self.driver.find_element(By.ID, "Ribbon.Permission.Modify.RemovePerms-Large")
      removeperm_button.click()
      self.driver.switch_to.alert.accept()
      sleep(5)
      giveperm_button = self.driver.find_element(By.ID, "Ribbon.Permission.Add.AddUser-Large")
      giveperm_button.click()
      sleep(2)      
      name_field = self.driver.find_element(By.XPATH, "//*[text()='Enter names or email addresses...']/following::input[@type='text']")
      if not real_data:
         address = 'alvin.gavel@arbetsförmedlingen.se'
      else:
         address = participant.code
      name_field.send_keys(address)
      name_field.send_keys(Keys.RETURN)
      sleep(2)
      #invite_field = self.driver.find_element(By.ID, "TxtEmailBody")  
      #if not real_data:
      #   invite_field.send_keys("Om detta inte varit ett simulerat test så skulle en text ha skrivits här och skickats till mailadressen {}. Nu skickas den till dig, för att bekräfta att mailandet fungerar.".format(participant.email))
      #else:
      #   invite_field.send_keys("Hej! Detta är ett test utfört av Alvin inom Demokratisk Digitalisering, för att testa om det går att överföra Canvas-användarnamn och lösenord via en SharePoint-sida, där varje deltagare får se en lista som innehåller deras eget användarnamn och lösenord. Nedan finns en länk till en sida som heter '{}' som innehåller ditt användarnamn och lösenord.".format(participant.name))
      #sleep(2)
      options_button = self.driver.find_element(By.ID, "Share_ShowHideMoreOptions")
      options_button.click()
      sleep(2)
      sendmail_button = self.driver.find_element(By.ID, "chkSendEmailv15")
      sendmail_button.click()
      sleep(2)
      options_list = self.driver.find_element(By.ID, "DdlGroup")
      options_list.click()
      sleep(2)
      read_choice = self.driver.find_element(By.XPATH, "//*[text()='Read']")
      read_choice.click()
      sleep(2)
      share_button = self.driver.find_element(By.ID, "btnShare")
      share_button.click()
      sleep(2)

class feedback_connection(SharePointConnection):
   """
   Used for writing passwords to SharePoint
   """
   def __init__(self, start_page_path, start_page_name, browser = 'Chrome', driver_directory_path = './Drivers'):
      SharePointConnection.__init__(self, start_page_path, start_page_name, browser = browser, driver_directory_path = driver_directory_path)
      return

   def deliver_feedback(self, participant, real_data):
      """
      This should make a page giving feedback to the participant, based on
      their results.
      """
      print('Began work at {}'.format(datetime.now().strftime('%X')))
      self.go_to_start()
      self.add_participant_as_member(participant, real_data)

      # Create a new page
      self.go_to_start()
      sleep(20)
      self.create_list("Feedback till {}".format(participant.name), participant)
      
      # Write feedback
      column_button = self.driver.find_element(By.XPATH, "//*[text()='Add column']")
      column_button.click()
      sleep(2)
      multiple_line_choice = self.driver.find_element(By.XPATH, "//*[text()='Multiple lines of text']")
      multiple_line_choice.click()
      sleep(2)
      name_field = self.driver.find_element(By.XPATH, "//*[text()='Name']/following::input[@type='text']")
      name_field.send_keys("Feedback")
      sleep(2)
      desc_field = self.driver.find_element(By.XPATH, "//*[text()='Description']/following::textarea")
      desc_field.send_keys("Feedback på de digitala kompetenserna")
      sleep(2)
      save_button = self.driver.find_element(By.CLASS_NAME, "ms-ColumnManagementPanel-saveButton")
      save_button.click()
      sleep(2)
      
      # Add entry for participant
      new_button = self.driver.find_element(By.XPATH, "//*[text()='New']")
      new_button.click()
      sleep(2)
      title_field = self.driver.find_element(By.XPATH, "//*[text()='Title']/following::input[@type='text'][position()=1]")
      title_field.send_keys('Hela kartläggningen')
      sleep(2)
      edit_button = self.driver.find_element(By.CSS_SELECTOR, "[aria-label='Edit']")
      edit_button.click()
      sleep(2)
      iframe = self.driver.find_element(By.TAG_NAME, "iframe")
      self.driver.switch_to.frame(iframe)
      sleep(2)
      text_field = self.driver.find_element(By.CSS_SELECTOR, "[aria-label='Rich text editor Feedback']")
      text_field.send_keys(participant.feedback_text)
      sleep(2)
      edit_button = self.driver.find_element(By.XPATH, "//*[text()='Edit']")
      edit_button.click()
      sleep(2)
      save_button = self.driver.find_element(By.XPATH, "//*[text()='Save']")
      save_button.click()
      sleep(2)
      # Exit the iframe again
      self.driver.switch_to.default_content()
      sleep(2)
      save_button = self.driver.find_element(By.XPATH, "//*[text()='Save']")
      save_button.click()
            
      self.set_read_privileges(participant, real_data)
      return


class password_connection(SharePointConnection):
   """
   Used for writing passwords to SharePoint
   """
   def __init__(self, start_page_path, start_page_name, browser = 'Chrome', driver_directory_path = './Drivers'):
      SharePointConnection.__init__(self, start_page_path, start_page_name, browser = browser, driver_directory_path = driver_directory_path)
      return
      
   def make_id_pwd_list(self, participant, real_data):
      """
      This should make a page with the user ID and password for one
      participant. However, note that this code is *very brittle* It could
      stop working at any moment due to some change of state in SharePoint
      that I do not understand.
      """
      print('Began work at {}'.format(datetime.now().strftime('%X')))
      self.go_to_start()      
      self.add_participant_as_member(participant, real_data)

      # Create a new list
      self.create_list("Canvas-användarnamn och lösenord till {}".format(participant.name), participant)
      
      # Make columns in the new page
      column_button = self.driver.find_element(By.XPATH, "//*[text()='Add column']")
      column_button.click()
      sleep(2)
      single_line_choice = self.driver.find_element(By.XPATH, "//*[text()='Single line of text']")
      single_line_choice.click()
      sleep(2)
      name_field = self.driver.find_element(By.XPATH, "//*[text()='Name']/following::input[@type='text']")
      name_field.send_keys("Användarnamn")
      sleep(2)
      desc_field = self.driver.find_element(By.XPATH, "//*[text()='Description']/following::textarea")
      desc_field.send_keys("Användarnamn till Canvas-kontot")
      sleep(2)
      save_button = self.driver.find_element(By.CLASS_NAME, "ms-ColumnManagementPanel-saveButton")
      save_button.click()
      sleep(2)
      column_button = self.driver.find_element(By.XPATH, "//*[text()='Add column']")
      column_button.click()
      sleep(2)
      single_line_choice = self.driver.find_element(By.XPATH, "//*[text()='Single line of text']")
      single_line_choice.click()
      sleep(2)
      name_field = self.driver.find_element(By.XPATH, "//*[text()='Name']/following::input[@type='text']")
      name_field.send_keys("Lösenord")
      sleep(2)
      desc_field = self.driver.find_element(By.XPATH, "//*[text()='Description']/following::textarea")
      desc_field.send_keys("Lösenord till Canvas-kontot")
      sleep(2)
      save_button = self.driver.find_element(By.CLASS_NAME, "ms-ColumnManagementPanel-saveButton")
      save_button.click()
      sleep(2)
      
      # Add entry for participant
      new_button = self.driver.find_element(By.XPATH, "//*[text()='New']")
      new_button.click()
      sleep(5)
      title_field = self.driver.find_element(By.XPATH, "//*[text()='Title']/following::input[@type='text'][position()=1]")
      title_field.send_keys(participant.name)
      sleep(2)
      userid_field = self.driver.find_element(By.XPATH, "//*[text()='Title']/following::input[@type='text'][position()=2]")
      userid_field.send_keys(participant.username)
      sleep(2)
      pwd_field = self.driver.find_element(By.XPATH, "//*[text()='Title']/following::input[@type='text'][position()=3]")
      pwd_field.send_keys(participant.password)
      sleep(2)
      save_button = self.driver.find_element(By.XPATH, "//*[text()='Save']")
      save_button.click()
      sleep(2)
      
      self.set_read_privileges(participant, real_data)
      print('Completed work at {}'.format(datetime.now().strftime('%X')))
      return

   def check_id_pwd_list(self, participant):
      """
      Verify that an already existing list for a participant has been written
      correctly.
      """
      print('Began work at {}'.format(datetime.now().strftime('%X')))
      self.go_to_start()
      try:
         sleep(5)
         list_button = self.driver.find_element(By.XPATH, "//*[text()='{}']".format(participant.name))
         list_button.click()
         sleep(5)
         self.driver.find_element(By.XPATH, "//*[text()='{}']".format(participant.username))
         self.driver.find_element(By.XPATH, "//*[text()='{}']".format(participant.password))
         verified = True
      except NoSuchElementException:
         verified = False
      print('Completed work at {}'.format(datetime.now().strftime('%X')))
      return verified
