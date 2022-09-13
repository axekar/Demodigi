"""
This script is intended to take the results from the learning module
IT-säkerhet and transform them into a format that can be handled by the
module factorial_experiment, which is stored one directory further up.

This course module is unusual in that it only has one session. Hence
there is no point in plotting have participants improve over
successive sessions.

This will create a directory named 'Results', with another directory
named 'Kartläggning' inside.
"""

import os
import preprocessing as pp

skills = ['WHF_Safety', 'Virus', 'TwoFactorAuthentication', 'Spam', 'SocialMedia', 'SafeEnvironments', 'Ransomware', 'PublicComputers', 'PortableDeviceSafety', 'PhoneFraud', 'Phishing', 'Password', 'PasswordManager', 'PUK', 'OpenNetworks', 'MacroVirus', 'InfoOverPhone', 'InfoOverInternet', 'Incognito', 'IMEI', 'GDRP_SensitivePersonalData', 'GDPR_Rights', 'GDPR_PersonalInformation', 'Cookies', 'Cache', 'Botnet', 'Backup']
mod = pp.learning_module(skills, n_sessions = 4)
mod.import_raw_analytics('OLI_analytics/IT-säkerhet/2022_09_31/raw_analytics.tsv') # This is temporary. It should not actually target a specific date.
mod.infer_participants_from_full_results()
mod.read_participants_results()
mod.describe_participants()

try:
   os.mkdir('Results')
except FileExistsError:
   pass
try:
   os.mkdir('Results/IT-säkerhet')
except FileExistsError:
   pass
mod.export_individual_results('Results/IT-säkerhet')
mod.export_IDs('Results/IT-säkerhet/IDs.json')
mod.export_SCB_data('Results/IT-säkerhet/SCB_data.csv')
