"""
This is a script that uses the Python module factorial_experiment to
read the results from the course module kartläggningsmodul, which must
in turn be created with the script PP_mapping_module_script in the
directory Utilities.
"""

import factorial_experiment as fe

skills = ['WifiProblems', 'TextFormating', 'Templates', 'SpotDeepFake', 'SolvingCrash', 'SoftwareFreeze', 'SharingPictures', 'SharingLargeFiles', 'SharingFiles', 'SharingEvents', 'SearchingForInfo', 'SafePasswords', 'Phishing', 'OrganisingFiles', 'OnlineMeetingProblems', 'MapServices', 'Malware', 'LearningAboutFunctions', 'InfoGraphics', 'ImageEditingSoftware', 'GDPR', 'FreeImages', 'FindingSolutions', 'EvaluateInformation', 'EmailFunctions', 'CreatingPresentations', 'CollaborationInDocuments', 'ChangingPDFs', 'Backup']

mod = fe.real_learning_module(len(skills), 1, 'Utilities/Results/Kartläggning/IDs.json', 'Utilities/Results/Kartläggning')
