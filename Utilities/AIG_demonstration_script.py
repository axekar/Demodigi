"""
This is a script for demonstrating how to use the module
account_info_generator.

The script simulates a group of ten participants and generates account
names and passwords for them. It requires there to be a directory named
Word_lists in the same directory as it is run, and this has to contain
a file named svenska which contains a list of words. It also requires a
directory named AIG_demo_files to put its data in.
"""

import account_info_generator as aig

# Output a file containing account data for the simulated participants
save_results = True

# Test that loading the participant data works
load_results = True

# Name of the directory where saved files will be put
save_directory = 'AIG_demo_files'

wordlist = aig.read_wordlist('Word_lists/Svenska')

account_info = aig.participant_list(wordlist, wordlist, password_length = 5)

account_info.simulate_participant_data(10)

account_info.generate_account_data()

if save_results:
   account_info.save_account_data('{}/account_data.csv'.format(save_directory))
   account_info.save_account_data_hashed('{}/account_data_hashed.csv'.format(save_directory))
   if load_results:
      account_info.save_participant_data('{}/participant_data.csv'.format(save_directory))
   
if load_results:
   loaded_info = aig.participant_list(wordlist, wordlist, password_length = 5)
   loaded_info.read_participant_data('{}/participant_data.csv'.format(save_directory))
   loaded_info.generate_account_data()
   if save_results:
      loaded_info.save_account_data('{}/participant_data_loaded_and_saved.csv'.format(save_directory))
