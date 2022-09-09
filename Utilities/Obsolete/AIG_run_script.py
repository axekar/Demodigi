"""
This is a script for running the module account_info_generator.

The script reads the contents of a file named Coacher.csv, which must
be in csv format with utf-8 encoding. It outputs four files of data,
which can be used by the other modules.
"""

import os
import account_info_generator as aig


# Name of the directory where saved files will be put
save_directory = 'Participant_data'

try:
   os.mkdir(save_directory)
except FileExistsError:
   pass

wordlist = aig.read_wordlist('Word_lists/Swedish_diceware_list.txt')

account_info = aig.participant_list(wordlist, password_length = 5)

account_info.read_participant_data_excel('Coacher.xlsx')

account_info.fill_in_data_fields()

account_info.save_account_IDs('{}/accounts.txt'.format(save_directory))
account_info.save_account_data('{}/account_data.csv'.format(save_directory))
account_info.save_account_data_hashed('{}/account_data_hashed.csv'.format(save_directory))
account_info.save_sharepoint_data('{}/sharepoint_data.csv'.format(save_directory))
