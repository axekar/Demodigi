"""
This script is intended for routine tasks related to the OLI Torus
module Kartläggning. It is also intended to clarify how to use the
Python modules created for the project. Hence, it has very verbose
comments.
"""

import datetime
import pytz

import sensitive_data_management as sdm
import preprocessing as pp
import canvas_contact as cc
import extra_functions as ef

ef.make_folder('Resultat')
ef.make_folder('Resultat/Kartläggning')
ef.make_folder('Resultat/Kartläggning/Individer')
ef.make_folder('Resultat/Kartläggning/Återkoppling')
ef.make_folder('Resultat/Kartläggning/Plottar')

# This takes the salt which gets used by the hash function to generate
# the usernames from the 5-character codes.
salt = input("Skriv in det salt som används vid hashningen som skapar användarnamnen:\n")

# We will need to read a list of data from the HR department. Right now
# we assume that it has a specific file name, so this will need to be
# updated if we get a more up-to-date list.
hr = sdm.HR_data(salt, "HR-data/Projekt demokratisk digitalisering 220921.xlsx", "Användardata")

# This is a dictionary describing the four competencies tested in the
# mapping module, and the individual skills that fall under each
# competence. Currently we do not give feedback on "Skapa och bearbeta
# digitalt innehåll", since we do not expect to have a learning module
# for that competence. Hence, that part is commented out, but can be
# commented in if our needs change.
competencies = {'Hitta och tolka digital information':['SearchingForInfo', 'MapServices', 'EvaluateInformation', 'SpotDeepFake', 'OrganisingFiles', 'SharingFiles'],
		'Kommunikation och samarbete':['EmailFunctions', 'SharingPictures', 'SharingEvents', 'CollaborationInDocuments',  'CreatingPresentations', 'SharingLargeFiles'],
		#'Skapa och bearbeta digitalt innehåll':['ImageEditingSoftware', 'InfoGraphics', 'TextFormating', 'Templates', 'ChangingPDFs', 'FreeImages'],
		'IT-säkerhet':['SafePasswords', 'Phishing', 'Malware', 'Backup', 'PortableDeviceSafety', 'GDPR'],
		'Problemlösning i digitala miljöer':['SoftwareFreeze', 'FindingSolutions', 'LearningAboutFunctions', 'WifiProblems', 'OnlineMeetingProblems', 'SolvingCrash']}

# For safety's sake, we toss out all results from earlier than the
# mapping officially started.
start_date = datetime.datetime(2022, 9, 27, tzinfo = pytz.UTC)

# We specify that the module has only one session - in contrast to the
# other modules where a central part of the pedagogy is the use of
# multiple sessions.
mod = pp.learning_module(competencies, n_sessions = 1, start_date = start_date, section_slug = 'kartlggning_av_digital_kompete_5arpp')

# We read the datashop file to get the participants' results. This may
# change if I can ever get the algorithm combining Datashop and raw_
# analytics to work.
mod.import_datashop('OLI_analytics/Kartläggning/datashop/Datashop_af_kartlggning_av_digital_komp.xml')

# We read the list of user names, which must previously have been
# created by the user_data_script
mod.read_participant_IDs('Användardata/Användarnamn.xlsx')
mod.read_participants_results(database = 'datashop')

# We get some terse text output describing the results on the module.
mod.describe_module()

### Export files

# Save a list of all participants.
mod.export_IDs('Resultat/Kartläggning/IDs.json')

# Data to be delivered to SCB, and also used when sending out reminders
# to participants who have not started yet.
mod.export_SCB_data('Resultat/Kartläggning/Prelim_SCB_data.csv')
hr.convert_SCB_data('Resultat/Kartläggning/Prelim_SCB_data.csv', 'Resultat/Kartläggning/SCB_data.xlsx')

# Save results to be read by the factorial_experiment module
mod.export_individual_results('Resultat/Kartläggning/Individer')

# Save files of feedback for each individual, which can then be sent to
# Canvas
mod.export_individual_feedback('Resultat/Kartläggning/Återkoppling')

# This currently cannot be used, since we do not have an algorithm that
# reliably tells us the performance of the individual participants
#mod.export_full_results('Resultat/Kartläggning/Full_results.csv')

# Make paedagogical plots to give us a hint of the results
mod.plot_results_by_time('Resultat/Kartläggning/Plottar')
mod.plot_initial_performance('Resultat/Kartläggning/Plottar')


### Upload Canvas feedback

# A token is necessary to demonstrate that you are an admin, with the
# right to send files to other users.
token = input("Fyll i en token till ett admin-konto på Canvas:\n")
message = 'Hej!\n\nDetta är din individuella återkoppling på kartläggningsmodulen.\n\nDetta är ett automatiserat meddelande och går inte att svara på.'

# We upload the feedback.
cc.send_feedback('Användardata/Användarnamn.xlsx', 'Resultat/Kartläggning/Återkoppling', 'alvin.gavel@arbetsformedlingen.se', 'Återkoppling på kartläggningsmodul', message, token, test = False, verbose = True)

# We create a list of mail adresses to the people who just received
# feedback.
today = datetime.today().strftime('%Y-%m-%d')
hr.emails_from_participant_list('Resultat/Kartläggning/Återkoppling/Tracker/Daily_deliveries/{}.txt'.format(today))
