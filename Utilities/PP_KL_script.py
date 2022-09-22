"""
This script is intended to take the results from the learning module
Kartläggning and transform them into a format that can be handled by
the module factorial_experiment, which is stored one directory further
up.

This course module is unusual in that it only has one session. Hence
there is no point in plotting how participants improve over
successive sessions.

This will create a directory named 'Results', with another directory
named 'Kartläggning' inside.
"""

import os
import datetime
import pytz

import preprocessing as pp

competencies = {'Hitta och tolka digital information':['SearchingForInfo', 'MapServices', 'EvaluateInformation', 'SpotDeepFake', 'OrganisingFiles', 'SharingFiles'],
		'Kommunikation och samarbete':['EmailFunctions', 'SharingPictures', 'SharingEvents', 'CollaborationInDocuments',  'CreatingPresentations', 'SharingLargeFiles'],
		#'Skapa och bearbeta digitalt innehåll':['ImageEditingSoftware', 'InfoGraphics', 'TextFormating', 'Templates', 'ChangingPDFs', 'FreeImages'],
		'IT-säkerhet':['SafePasswords', 'Phishing', 'Malware', 'Backup', 'PortableDeviceSafety', 'GDPR'],
		'Problemlösning i digitala miljöer':['SoftwareFreeze', 'FindingSolutions', 'LearningAboutFunctions', 'WifiProblems', 'OnlineMeetingProblems', 'SolvingCrash']}

start_date = datetime.datetime(2022, 9, 18, tzinfo = pytz.UTC)
end_date = datetime.datetime(2022, 9, 23, tzinfo = pytz.UTC)
mod = pp.learning_module(competencies, n_sessions = 1, start_date = start_date, end_date = end_date, section_slug = 'kartlggning_av_digital_kompete_5arpp')

# This is temporary. It should not actually target a specific date.
mod.import_data('OLI_analytics/Kartläggning/2022_09_22/raw_analytics.tsv', 'OLI_analytics/Kartläggning/2022_09_22/Datashop_af_kartlggning_av_digital_komp.xml', verbose = True)

mod.read_participant_IDs('Participant_data/Coaches.txt')
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
   os.mkdir('Results/Kartläggning/Individer')
except FileExistsError:
   pass
try:
   os.mkdir('Results/Kartläggning/Återkoppling')
except FileExistsError:
   pass
try:
   os.mkdir('Results/Kartläggning/Plottar')
except FileExistsError:
   pass
mod.export_individual_results('Results/Kartläggning/Individer')
mod.export_individual_feedback('Results/Kartläggning/Återkoppling')
mod.export_IDs('Results/Kartläggning/IDs.json')
mod.export_mapping('Results/Kartläggning/Mapping.csv')
mod.export_SCB_data('Results/Kartläggning/SCB_data.csv')
mod.export_full_results('Results/Kartläggning/Full_results.csv')
mod.plot_results_by_time('Results/Kartläggning/Plottar')
mod.plot_initial_performance('Results/Kartläggning/Plottar')
