"""
This is a script that uses the Python module factorial_experiment to
read the results from the course module kartläggningsmodul, which must
in turn be created with the script PP_mapping_module_script in the
directory Utilities.
"""

import factorial_experiment as fe

skills = ['WHF_Safety', 'Virus', 'TwoFactorAuthentication', 'Spam', 'SocialMedia', 'SafeEnvironments', 'Ransomware', 'PublicComputers', 'PortableDeviceSafety', 'PhoneFraud', 'Phishing', 'Password', 'PasswordManager', 'PUK', 'OpenNetworks', 'MacroVirus', 'InfoOverPhone', 'InfoOverInternet', 'Incognito', 'IMEI', 'GDRP_SensitivePersonalData', 'GDPR_Rights', 'GDPR_PersonalInformation', 'Cookies', 'Cache', 'Botnet', 'Backup']

mod = fe.real_learning_module(len(skills), 4, 'Utilities/Results/IT-säkerhet/IDs.json', 'Utilities/Results/IT-säkerhet', manipulation_path = 'Utilities/Results/Användardata/Manipulations.json')
trial_study = fe.study('IT-säkerhet', mod)
trial_study.describe()
trial_study.do_tests()
trial_study.summarise_results()
