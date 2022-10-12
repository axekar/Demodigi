"""
This script is intended for the routine task of creating users on Canvas
and giving them access to courses.
"""

import sensitive_data_management as sdm
import extra_functions as ef

ef.make_folder('Användardata')

# This takes the salt which gets used by the hash function to generate
# the usernames from the 5-character codes.
salt = input("Skriv in det salt som används vid hashningen som skapar användarnamnen:\n")

# This takes the path to the file with the user information
path = input("Skriv in den relativa sökvägen till HR-filen med deltagarnamnet:\n")

# We will need to read a list of data from the HR department. Right now
# we assume that it has a specific file name, so this will need to be
# updated if we get a more up-to-date list.
hr = sdm.HR_data(salt, path, "Användardata")

# This generates a large number of useful files based on the user data.
hr.make_SIS_data()
hr.export_SIS_data()
