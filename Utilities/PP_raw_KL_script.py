"""
This script is intended to take the results from the learning module
Kartläggning and transform them into a format that can be handled by
the module factorial_experiment, which is stored one directory further
up. It assumes that the results are in the raw_analytics format, rather
than XML.

This course module is unusual in that it only has one session. Hence
there is no point in plotting how participants improve over
successive sessions.

This will create a directory named 'Results', with another directory
named 'Kartläggning' inside.
"""

import os
import preprocessing as pp

competencies = {'Hitta och tolka digital information':['SearchingForInfo', 'MapServices', 'EvaluateInformation', 'SpotDeepFake', 'OrganisingFiles', 'SharingFiles'],
		'Kommunikation och samarbete':['EmailFunctions', 'SharingPictures', 'SharingEvents', 'CollaborationInDocuments',  'CreatingPresentations', 'SharingLargeFiles'],
		'Skapa och bearbeta digitalt innehåll':['ImageEditingSoftware', 'InfoGraphics', 'TextFormating', 'Templates', 'ChangingPDFs', 'FreeImages'],
		'IT-säkerhet':['SafePasswords', 'Phishing', 'Malware', 'Backup', 'PortableDeviceSafety', 'GDPR'],
		'Problemlösning i digitala miljöer':['SoftwareFreeze', 'FindingSolutions', 'LearningAboutFunctions', 'WifiProblems', 'OnlineMeetingProblems', 'SolvingCrash']}
		
mod = pp.learning_module(competencies, n_sessions = 1)
mod.import_raw_analytics('OLI_analytics/Kartläggning/2022_09_02/raw_analytics.tsv', section_slug = 'kartlggning_av_digital_kompete') # This is temporary. It should not actually target a specific date.
mod.infer_participants_from_full_results()
mod.read_participants_results()
mod.describe_module()

try:
   os.mkdir('Results')
except FileExistsError:
   pass
try:
   os.mkdir('Results/Kartläggning')
except FileExistsError:
   pass
try:
   os.mkdir('Results/Kartläggning/Plottar_raw')
except FileExistsError:
   pass
try:
   os.mkdir('Results/Kartläggning/Individer_raw')
except FileExistsError:
   pass
mod.export_results('Results/Kartläggning/Individer_raw')
mod.export_IDs('Results/Kartläggning/Raw_IDs.json')
mod.export_SCB_data('Results/Kartläggning/SCB_data.csv')
mod.export_full_results('Results/Kartläggning/Raw_to_csv.csv')
mod.plot_results_by_time('Results/Kartläggning/Plottar_raw')
