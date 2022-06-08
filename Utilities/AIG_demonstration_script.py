"""
This is a script for demonstrating how to use the module
account_info_generator.

The script simulates a group of ten participants and generates account
names and passwords for them. It requires there to be a directory named
Word_lists in the same directory as it is run, and this has to contain
a file named svenska which contains a list of words.
"""

import account_info_generator as aig

# Output a file containing account data for the simulated participants
save_results = True

# Test that loading the participant data works
load_results = True

wordlist = aig.read_wordlist('Word_lists/Svenska')

account_info = aig.participant_list(wordlist, wordlist, password_length = 5)

account_info.simulate_participants(10)

account_info.generate_account_data()

if save_results:
   account_info.save_data('simulated_participants_account_data.csv')
   if load_results:
      account_info.save_simulated_participants('simulated_participants_person_data.csv')
   
if load_results:
   account_info_about_loaded_participants = aig.participant_list(wordlist, wordlist, password_length = 5)
   account_info_about_loaded_participants.read_participant_data('simulated_participants_person_data.csv')
   account_info_about_loaded_participants.generate_account_data()
   if save_results:
      account_info_about_loaded_participants.save_data('loaded_participants_account_data.csv')
