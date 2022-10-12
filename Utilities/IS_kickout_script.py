"""
This script is intended for the task of removing everyone from the
teaching module IT-säkerhet. I needed to use this due to a mishap
where I gave everyone access to a specific version of the course,
when we actually wanted to have them divided over several versions.
I am keeping the script around in case it comes in handy again,
perhaps for other courses.
"""

import sensitive_data_management as sdm
import extra_functions as ef

ef.make_folder('Användardata')
ef.make_folder('Användardata/IT-säkerhet')

# This takes the salt which gets used by the hash function to generate
# the usernames from the 5-character codes.
salt = input("Skriv in det salt som används vid hashningen som skapar användarnamnen:\n")

# We will need to read a list of data from the HR department. Right now
# we assume that it has a specific file name, so this will need to be
# updated if we get a more up-to-date list.
hr = sdm.HR_data(salt, "HR-data/Projekt demokratisk digitalisering 220921.xlsx", "Användardata/IT-säkerhet")

# This generates a large number of useful files based on the user data.
hr.make_SIS_kickout_file('111')
