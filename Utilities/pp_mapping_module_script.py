"""
This script is intended to take the results from the 
"""

import preprocessing as pp

skills = ['WifiProblems', 'TextFormating', 'Templates', 'SpotDeepFake', 'SolvingCrash', 'SoftwareFreeze', 'SharingPictures', 'SharingLargeFiles', 'SharingFiles', 'SharingEvents', 'SearchingForInfo', 'SafePasswords', 'Phishing', 'OrganisingFiles', 'OnlineMeetingProblems', 'MapServices', 'Malware', 'LearningAboutFunctions', 'InfoGraphics', 'ImageEditingSoftware', 'GDPR', 'FreeImages', 'FindingSolutions', 'EvaluateInformation', 'EmailFunctions', 'CreatingPresentations', 'CollaborationInDocuments', 'ChangingPDFs', 'Backup']
mod = pp.learning_module(skills)
mod.import_oli_results('OLI_analytics/2022_09_31/raw_analytics.tsv')
mod.infer_participants_from_full_results()
mod.read_participants_results()
mod.describe_participants()

mod.export_results('Results')
