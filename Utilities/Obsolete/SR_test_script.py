"""
This is a script for testing those functions in the module
sharepoint_robot that do not require actually starting up a web browser
and accessing a SharePoint page.
"""

import sharepoint_robot as sr

cnct = sr.password_connection('dummy page path', 'dummy page name')


print("Testing password_clicker...")
robot_passwords = sr.password_clicker(cnct)
n_participants = 29
robot_passwords.simulate_participant_list(n_participants)
correct_number = len(robot_passwords.participants) == n_participants

if not correct_number:
   print('simulate_participant_list makes wrong number of participants')
if correct_number:
   print('password_clicker passed tests!')
   
   
print("Testing feedback_clicker...")
robot_feedback = sr.feedback_clicker(cnct)
n_participants = 29
robot_feedback.simulate_participant_list(n_participants)
correct_number = len(robot_feedback.participants) == n_participants

if not correct_number:
   print('simulate_participant_list makes wrong number of participants')
if correct_number:
   print('feedback_clicker passed tests!')
