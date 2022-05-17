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
particpant, meaning that it should be connected to their AF account.

Since the project will have around 8000-11000 participants, we do not
want to create these lists manually. Unfortunately, we do not have any
automatic way of creating pages in SharePoint. Hence, our solution is
to use Selenium to implement a "robot" that creates the SharePoint
lists.

Running the module currently requires Chrome/Chromium, although it is
probably trivial to modify it to use Firefox. By default the module
assumes that the drivers are stored in a directory named "Drivers".

Written by Alvin Gavel,
https://github.com/Alvin-Gavel/Demodigi
"""

import selenium as sl
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

import numpy as np
import csv
from datetime import datetime
from time import sleep

class participant():
   """
   A person who participates in a learning module, to whom we want to
   deliver Canvas account information to.
   
   Attributes
   ----------
   name : str
   \tName of the particpant. This may be replaced with the 5-character code
   \tused at AF
   email : str
   \tJob e-mail address
   username : str
   \tName of Canvas account
   password : str
   \tPassword to Canvas account
   """
   def __init__(self, name, email, username, password):
      self.name = name
      self.email = email
      self.username = username
      self.password = password
      return

class clicker:
   """
   A device that reads lists of our participants and writes them to the
   SharePoint page - or instead reads an already finished SharePoint page
   and compares it to a list of participants.
   
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
   
   def read_participant_list(self, path):
      """
      Reads a csv-file of participants, in the format
      name, email, username, password
      """
      f = open(path, 'r', newline='')
      reader = csv.reader(f, delimiter = ',')
      self.participants = []
      for line in reader:
         name = line[0].strip()
         email = line[1].strip()
         username = line[2].strip()
         password = line[3].strip()
         self.participants.append(participant(name, email, username, password))
      f.close()
      
      self.real_data = True
      return
   
   def simulate_participant_list(self, n_participants):
      """
      Generate a list of pretended particpants
      """
      self.participants = []
      for i in range(n_participants):
         self.participants.append(participant('Robot {}'.format(i), 'rob{}@skynet.com'.format(i), 'usr{}'.format(i), '123456'))
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
      
   def read_sharepoint_lists(self):
      """
      Read lists that have already been constructed on SharePoint, so that
      they can be compared to a list on file to verify that the SharePoint
      lists are correct.
      """
      pass
      return


class SharepointConnection(object):
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
   def __init__(self, start_page_path, start_page_name, browser = 'Chrome', driver_directory_path = './Drivers'):
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

   def make_id_pwd_list(self, participant, real_data):
      """
      This should make a page with the user ID and password for one
      participant. However, note that this code is *very brittle* It could
      stop working at any moment due to some change of state in SharePoint
      that I do not understand.
      """
      print('Began work at {}'.format(datetime.now().strftime('%X')))
      self.go_to_start()
      sleep(5)
      new_button = self.driver.find_element(By.NAME, "New")
      new_button.click()
      sleep(2)
      list_choice = self.driver.find_element(By.NAME, "List")
      list_choice.click()
      sleep(2)
      name_field = self.driver.find_element(By.XPATH, "//*[text()='Name']/following::input[@type='text']")
      name_field.send_keys("Konto-info för {}".format(participant.name))
      sleep(2)
      desc_field = self.driver.find_element(By.XPATH, "//*[text()='Description']/following::textarea")
      desc_field.send_keys("Canvas-användarnamn och lösenord till {}".format(participant.name))
      sleep(2)
      create_button = self.driver.find_element(By.CSS_SELECTOR, "[aria-label=Create]")
      create_button.click()
      sleep(10)
      
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
      sleep(2)
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
      
      # Set read privileges
      create_button = self.driver.find_element(By.CSS_SELECTOR, "[aria-label='Open the Settings menu to access personal and app settings']")
      create_button.click()
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
         address = participant.email
      name_field.send_keys(address)
      name_field.send_keys(Keys.RETURN)
      sleep(2)
      invite_field = self.driver.find_element(By.ID, "TxtEmailBody")  
      if not real_data:
         invite_field.send_keys("Om detta inte varit ett simulerat test så skulle en text ha skrivits här och skickats till mailadressen {}. Nu skickas den till dig, för att bekräfta att mailandet fungerar.".format(participant.email))
      else:
         invite_field.send_keys("Hej! Detta är ett test utfört av Alvin inom Demokratisk Digitalisering, för att testa om det går att överföra Canvas-användarnamn och lösenord via en SharePoint-sida, där varje deltagare får se en lista som innehåller deras eget användarnamn och lösenord. Nedan finns en länk till en sida som heter 'Konto-info för {}'. När du har tid, klicka på den länken och kolla om du kan se ett (påhittat) användarnamn och lösenord, och gärna också att du inte kan se detta för någon annan än dig själv.".format(participant.name))
      sleep(2)
      options_button = self.driver.find_element(By.ID, "Share_ShowHideMoreOptions")
      options_button.click()
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
      print('Completed work at {}'.format(datetime.now().strftime('%X')))
      return
