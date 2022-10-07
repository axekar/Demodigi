"""
This script is intended to take results 
"""

import os
import datetime
import pytz

import sensitive_data_management as sdm
import preprocessing as pp
import canvas_contact as cc

try:
   os.mkdir('Resultat')
except FileExistsError:
   pass
try:
   os.mkdir('Resultat/Kartläggning')
except FileExistsError:
   pass
try:
   os.mkdir('Resultat/Kartläggning/Individer')
except FileExistsError:
   pass
try:
   os.mkdir('Resultat/Kartläggning/Återkoppling')
except FileExistsError:
   pass
try:
   os.mkdir('Resultat/Kartläggning/Plottar')
except FileExistsError:
   pass

salt = input("Skriv in det salt som används vid hashningen som skapar användarnamnen:\n")
try:
   os.mkdir('Användardata')
except FileExistsError:
   pass
hr = sdm.HR_data(salt, "HR-data/Projekt demokratisk digitalisering 220921.xlsx", "Användardata")
hr.generate_data()

competencies = {'Hitta och tolka digital information':['SearchingForInfo', 'MapServices', 'EvaluateInformation', 'SpotDeepFake', 'OrganisingFiles', 'SharingFiles'],
		'Kommunikation och samarbete':['EmailFunctions', 'SharingPictures', 'SharingEvents', 'CollaborationInDocuments',  'CreatingPresentations', 'SharingLargeFiles'],
		#'Skapa och bearbeta digitalt innehåll':['ImageEditingSoftware', 'InfoGraphics', 'TextFormating', 'Templates', 'ChangingPDFs', 'FreeImages'],
		'IT-säkerhet':['SafePasswords', 'Phishing', 'Malware', 'Backup', 'PortableDeviceSafety', 'GDPR'],
		'Problemlösning i digitala miljöer':['SoftwareFreeze', 'FindingSolutions', 'LearningAboutFunctions', 'WifiProblems', 'OnlineMeetingProblems', 'SolvingCrash']}

start_date = datetime.datetime(2022, 9, 27, tzinfo = pytz.UTC)
mod = pp.learning_module(competencies, n_sessions = 1, start_date = start_date, section_slug = 'kartlggning_av_digital_kompete_5arpp')

mod.import_datashop('OLI_analytics/Kartläggning/datashop/Datashop_af_kartlggning_av_digital_komp.xml')

mod.read_participant_IDs('Användardata/Användarnamn.xlsx')
mod.read_participants_results(database = 'datashop')
mod.describe_module()

mod.export_IDs('Resultat/Kartläggning/IDs.json')
mod.export_SCB_data('Resultat/Kartläggning/Prelim_SCB_data.csv')
hr.convert_SCB_data('Resultat/Kartläggning/Prelim_SCB_data.csv', 'Resultat/Kartläggning/SCB_data.xlsx')
mod.export_individual_results('Resultat/Kartläggning/Individer')
mod.export_individual_feedback('Resultat/Kartläggning/Återkoppling')
mod.export_full_results('Resultat/Kartläggning/Full_results.csv')
mod.plot_results_by_time('Resultat/Kartläggning/Plottar')
mod.plot_initial_performance('Resultat/Kartläggning/Plottar')

token = input("Fyll i en token till ett admin-konto på Canvas:\n")
message = 'Hej!\n\nDetta är din individuella återkoppling på kartläggningsmodulen.\n\nDetta är ett automatiserat meddelande och går inte att svara på.'

cc.send_feedback('Användardata/Användarnamn.xlsx', 'Resultat/Kartläggning/Återkoppling', 'alvin.gavel@arbetsformedlingen.se', 'Återkoppling på kartläggningsmodul', message, token, test = False, verbose = True)

today = datetime.today().strftime('%Y-%m-%d')
hr.emails_from_participant_list('Resultat/Kartläggning/Återkoppling/Tracker/Daily_deliveries/{}.txt'.format(today))
