"""
This script is intended for the routine task of creating users on Canvas
and giving them access to courses.
"""

import sensitive_data_management as sdm
import extra_functions as ef

ef.make_folder('Användardata')
ef.make_folder('Användardata/Kartläggning')

# This takes the salt which gets used by the hash function to generate
# the usernames from the 5-character codes.
salt = input("Skriv in det salt som används vid hashningen som skapar användarnamnen:\n")

# We will need to read a list of data from the HR department. Right now
# we assume that it has a specific file name, so this will need to be
# updated if we get a more up-to-date list.
hr = sdm.HR_data(salt, "HR-data/Projekt demokratisk digitalisering 220921.xlsx", "Användardata/Kartläggning")

# This generates a large number of useful files based on the user data.
hr.generate_data()
