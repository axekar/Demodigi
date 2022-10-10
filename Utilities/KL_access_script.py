"""
This script is intended for the routine task of giving course access on
Canvas to users who have for some reason lost it. We believe this is
typically caused by users accidentally clicking away the course
invitation, but it could also be due to some internal problem in Canvas,
since we handle much larger numbers of users than is normal.
"""

import sensitive_data_management as sdm

# This takes the salt which gets used by the hash function to generate
# the usernames from the 5-character codes.
salt = input("Skriv in det salt som används vid hashningen som skapar användarnamnen:\n")

# We will need to read a list of data from the HR department. Right now
# we assume that it has a specific file name, so this will need to be
# updated if we get a more up-to-date list.
hr = sdm.HR_data(salt, "HR-data/Projekt demokratisk digitalisering 220921.xlsx", "Användardata")

emails = input("Skriv in jobbmailaddresserna, skilda med kommatecken och mellanslag, för personerna som behöver få access till lärmodulen på Canvas:\n")
print('')

IDs = hr.transform_real_email_to_fake(emails, ['Default'])
print('\nKlipp-och-klistra följande mailaddresser till Canvas-sidan för kartläggningsmodulen:')
print(IDs['Default'])
print('')
