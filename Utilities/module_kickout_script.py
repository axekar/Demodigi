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

user_data_path = 'Användardata/'
user_removal_path = user_data_path + 'Borttagningsfiler/'

ef.make_folder(user_data_path)
ef.make_folder(user_removal_path)

# This takes the salt which gets used by the hash function to generate
# the usernames from the 5-character codes.
salt = input("Skriv in det salt som används vid hashningen som skapar användarnamnen:\n")

# We will need to read a list of data from the HR department.
HR_path = input("Skriv in sökvägen till en fil som innehåller alla användare som ska tas bort. (Filen måste följa exakt samma format som filen från HR-avdelningen):\n")

hr = sdm.HR_data(salt, HR_path, user_removal_path)

SIS_ID = input("Skriv in SID-ID för kursen. (Finns under 'Inställningar' för kursen på Canvas. Om kursen inte har ett SIS-ID, ge den ett):\n")

# Generate a csv-file that can be uploaded to canvas using SIS-import, which
# will remove all the specified users from the course.
hr.make_SIS_kickout_file(SIS_ID)

print('Det finns nu en fil i mappen {} som heter enrollments.csv. Gå in på Canvas och välj SIS Import, och ladda upp filen. Användarna kommer nu att tas bort från kursen.'.format(user_removal_path))
