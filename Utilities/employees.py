"""
This script was written for the ESF-financed project Demokratisk
Digitalisering. The project is a collaboration between
Arbetsförmedlingen (AF) and Kungliga Tekniska Högskolan (KTH). The
purpose of the project is to increase the digital competence - as
defined at https://ec.europa.eu/jrc/en/digcomp - of people working at
Arbetsförmedlingen and by extension also job seekers. This will be
done by learning modules at KTH using OLI-Torus.

--- About this Python script ---

This script is intended to help us figure out who actually works at AF,
and what department they are in. The best approach we have found so far
is to use Microsoft Access to extract the list of global contacts
stored in Microsoft Outlook, and then export that as a Microsoft Excel
file. Unfortunately, that file has some problems, namely:

 - Many entries are not actual people. For example, rooms also have
   email adresses.

 - 'Organisatorisk tillhörighet' is written in a format that differs
   from the official, and only includes one of the three levels of AF's
   organisational hierarchy.

The purpose of this script is to convert the Excel file returned by
MS Access into a CSV file with exactly the data we want. This being:

 - First name
 
 - Last name
 
 - Five-character code
 
 - 'Organisatorisk tillhörighet', on all three levels in the AF
   organisational hierarchy

Written by Alvin Gavel
https://github.com/Alvin-Gavel/Demodigi
"""

import pandas as pd
import numpy as np

## The organisational structure of AF, according to our own internal web
## pages

sub_of_seek = ['Avdelningen Stärka förutsättningar', 'Region mitt', 'Region nord', 'Region Stockholm Gotland', 'Region syd', 'Region väst', 'Region öst']
sub_of_give = ['Avdelningen Arbetsgivare och leverantörer', 'Region mitt', 'Region nord', 'Region Stockholm Gotland', 'Region syd', 'Region väst', 'Region öst']

# The highest level of organisation, excluding sök and AG
super_to_sub = {
'Ledning och staber':['Styrelsen', 'Generaldirektören', 'Överdirektören', 'Generaldirektörens ledningsgrupp', 'Ledningsstaben', 'Internrevisionen', 'Staben Strategisk förändring'],
'VO Arbetssökande':sub_of_seek,
'VO Arbetsgivare':sub_of_give,
'VO Direkt':['Avdelningen Digitala tjänster', 'Avdelningen Kundsupport och ersättning', 'Avdelningen Personligt distansmöte', 'Enheten Jobtech', 'Sektionen Digitalt engagemang', 'Utvecklingsavdelningen för kundmötet'],
'VO It':['Avdelningen Data science och digitala plattformar', 'Enheten Cybersäkerhet och digital tillit', 'Enheten Digitala beslut och ärenden', 'Enheten Digitalt fördjupat stöd och fristående aktörer', 'Enheten It för personligt distansmöte och kontroll', 'Enheten It infrastruktur', 'Enheten Myndighetsgemensam it', 'Enheten Rådgivning', 'Enheten Samband och effekter'],
'Analysavdelningen':['Enheten Arbetsmarknad', 'Enheten Utvärdering'],
'Ekonomiavdelningen':['Enheten Ekonomistyrning', 'Enheten Redovisning och rapportering', 'Enheten Uppföljning och kontroll', 'Enheten Utveckling och förvaltning'],
'Förvaltningsavdelningen':['Enheten Affärsområde arbetsmarknadstjänster','Enheten Affärsområde it och förvaltning','Enheten Affärsstöd','Enheten Lokalförsörjning','Enheten Samordnade tjänster','Säkerhetsenheten'],
'HR-avdelningen':['Enheten Arbetsmiljö och hälsa','Enheten Arbetsrätt och lönebildning','Enheten Chefsutveckling','Enheten HR Nationellt stöd','Enheten HR Verksamhetsnära stöd - VO Arbetsgivare och VO Arbetssökande','Enheten HR Verksamhetsnära stöd - VO Direkt, VO It och huvudkontoret','Enheten Kompetensförsörjning'],
'Kommunikationsavdelningen':['Enheten Kund och marknad','Enheten Myndighet och ledning','Enheten Nyhetsdesk och mediacenter','Enheten Verksamhetsutveckling'],
'Rättsavdelningen':['Enheten Arbetsmarknad och arbetsrätt','Enheten Avtal, it och förvaltningsrätt','Enheten God förvaltning','Enheten Informationsförvaltning','Enheten Omprövning','Enheten Programjuridik','Enheten Riktning och stöd']
}

# The connection between the second to the third level of organisation,
# excluding sök and AG
sub_to_subsub_other = {
'Överdirektören':['Enheten styrning och uppföljning'],
'Ledningsstaben':['Enheten Nationell samordning Eures', 'Enheten Strategiskt stöd', 'Internationella enheten', 'Kansliet'],
'Avdelningen Stärka förutsättningar':['Enheten Arbetsmarknadsinsatser', 'Enheten Riktade insatser', 'Enheten Utbilda och samverka'],
'Avdelningen Arbetsgivare och leverantörer':['Enheten Kompetensförsörjning och arbetsgivarstöd', 'Enheten Leverantörsuppföljning', 'Enheten Tjänsteutveckling leverantör'],
'Avdelningen Digitala tjänster':['Enheten Rusta och matcha', 'Enheten rehabilitera', 'Enheten Vägleda och utbilda', 'Enheten Inskriva, planera och bedöma', 'Enheten Arbetsmarknadsbedömning'],
'Avdelningen Kundsupport och ersättning':['Enheten Ersättningar', 'Enheten Ersättningsprövning', 'Enheten Kultur media', 'Enheten Kundsupport', 'Enheten Granskning och kontroll Norrköping', 'Enheten Granskning och kontroll Falun', 'Enheten Granskning och kontroll Köping', 'Samordning servicekontor'],
'Avdelningen Personligt distansmöte':['Enheten Bemanning och verksamhetsanalys', 'Enheten Beslut och service', 'Enheten Kundadministration och support', 'Enheten Verksamhetsutveckling', 'Enheten Göteborg, Frölunda, Arvidsjaur', 'Enheten Östersund, Sundsvall, Söderhamn', 'Enheten Malmö Karlskrona', 'Enheten Stockholm', 'Enheten Södertälje, Sollefteå', 'Enheten Örebro, Karlskoga, Skara', 'Enheten Luleå, Lycksele'],
'Utvecklingsavdelningen för kundmötet':['Enheten för kundarbete', 'Enheten för kundupplevelse'],
'Avdelningen Data science och digitala plattformar':['Enheten Datadriven analys och AI', 'Enheten Data och informationsstyrning', 'Enheten Upplevelse och ny teknik']
}

# The connection between the second to the third level of organisation,
# specifically at sök
sub_to_subsub_seek = {
'Avdelningen Stärka förutsättningar':['Enheten Arbetsmarknadsinsatser', 'Enheten Riktade insatser', 'Enheten Utbilda och samverka'],
'Region mitt':['Enheten Dalarna', 'Enheten Gävleborg', 'Enheten Södermanland', 'Enheten Uppsala', 'Enheten Värmland', 'Enheten Västmanland', 'Enheten Örebro'],
'Region nord':['Enheten Jämtland Härjedalen', 'Enheten Norra Norrbotten', 'Enheten Norra Västerbotten', 'Enheten Norra Västernorrland', 'Enheten Sydöstra Västerbotten', 'Enheten Södra Norrbotten', 'Enheten Södra Västernorrland'],
'Region Stockholm Gotland':['Enheten Gotland', 'Enheten Huddinge Botkyrka', 'Enheten Nordvästra Stockholm', 'Enheten Nordöstra Stockholm', 'Enheten Stockholm stad City Vällingby', 'Enheten Stockholm stad Globen Liljeholmen Skärholmen', 'Enheten Stockholm stad Järva', 'Enheten Sydöstra Stockholm', 'Enheten Södertälje'],
'Region syd':['Enheten Blekinge', 'Enheten Kronoberg', 'Enheten Malmö', 'Enheten Nordvästra Skåne', 'Enheten Sydvästra Skåne', 'Enheten Östra Skåne'],
'Region väst':['Enheten Fyrbodal', 'Enheten Halland', 'Enheten Norra Göteborg', 'Enheten Sjuhärad', 'Enheten Skaraborg', 'Enheten Södra Göteborg', 'Enheten Östra Göteborg'],
'Region öst':['Enheten Jönköping', 'Enheten Kalmar', 'Enheten Regionstab', 'Enheten Östergötland'],
}

# The connection between the second to the third level of organisation,
# specifically at AG
sub_to_subsub_give = {
'Avdelningen Arbetsgivare och leverantörer':['Enheten Kompetensförsörjning och arbetsgivarstöd', 'Enheten Leverantörsuppföljning', 'Enheten Tjänsteutveckling leverantör'],
'Region mitt':['Enheten Dalarna', 'Enheten Gävleborg', 'Enheten Södermanland', 'Enheten Uppsala', 'Enheten Värmland', 'Enheten Västmanland', 'Enheten Örebro'],
'Region nord':['Enheten Jämtland Härjedalen', 'Enheten Norrbotten', 'Enheten Västerbotten', 'Enheten Västernorrland'],
'Region Stockholm Gotland':['Enheten Norra Stockholm Gotland', 'Enheten Regiongemensamma Uppdrag', 'Enheten Stockholm stad', 'Enheten Södra Stockholm'],
'Region syd':['Enheten Beslut och uppföljning', 'Enheten Kronoberg Blekinge', 'Enheten Malmö', 'Enheten Nordvästra Skåne', 'Enheten Östra Skåne'],
'Region väst':['Enheten Fyrbodal', 'Enheten Halland Sjuhärad', 'Enheten Nordöstra Göteborg', 'Enheten Skaraborg', 'Enheten Sydöstra Göteborg'],
'Region öst':['Enheten Jönköping', 'Enheten Kalmar', 'Enheten Regionstab', 'Enheten Östergötland'],
}

# The connection between the second to the third level of organisation
sub_to_subsub = {'Arbetssökande':sub_to_subsub_seek, 'Arbetsgivare':sub_to_subsub_give, 'Övrigt':sub_to_subsub_other}

# Define the connection from the second to first level of organisation,
# excluding sök and AG
sub_to_super = {'???':'???'}
for super_org, sub_orgs in super_to_sub.items():
   for sub_org in sub_orgs:
      sub_to_super[sub_org] = super_org

# Define the connection from the third to second level of organisation
subsub_to_sub = {}
for key in sub_to_subsub.keys():
   subsub_to_sub[key] = {}
   for sub_org, subsub_orgs in sub_to_subsub[key].items():
      for subsub_org in subsub_orgs:
         subsub_to_sub[key][subsub_org] = sub_org

## Functions for identifying organisational position

def compare_parts(parts_1, parts_2):
   """
   Figure out if two text strings divided into pieces (typically the
   division is done at whitespace) are identical
   """
   match = True
   if len(parts_1) == len(parts_2):
      for part_1, part_2 in zip(parts_1, parts_2):
         match = match and part_1 == part_2[:len(part_1)]
   else:
      match = False
   return match

def lengthen_common_abbreviations(abbreviation):
   return abbreviation.replace('reg ', 'regionalt ').replace('omr ', 'område ').replace('enh ', 'enheten ').replace('avd ', 'avdelningen ').replace('sundsv ', 'sundsvall ').replace('sunds ', 'sundsvall ').replace('sthlm', 'stockholm').replace(' hk', ' huvudkontoret').replace('kontr ', 'kontroll ').replace('pdm', 'personligt distansmöte').replace('pers distansmöte', 'personligt distansmöte').replace('dir ', 'direkt ').replace('vsamhetsanalys', 'verksamhetsanalys').replace('cybersäkh', 'cybersäkerhet').replace('ersättn', 'ersättning').replace('ersättninging', 'ersättning').replace(' upplevelser', ' upplevelse')

def lengthen_abbreviations_specific_to_seek(abbreviation):
   return abbreviation.replace(' as', ' arbetssökande').replace('kramf sollefteå örnsköldsv', 'norra västernorrland').replace(' glo', ' globen').replace(' lilj', ' liljeholmen').replace(' skär', ' skärholmen')

def lengthen_abbreviations_specific_to_give(abbreviation):
   return abbreviation.replace(' ag', ' arbetsgivare')

def remove_connectives(abbreviation):
   return abbreviation.replace('-', ' ').replace('för ', '').replace('och ', '').replace(' chef', '').replace('biträdande', '').replace('bitr', '').replace(' stab', '').replace('stab ', '').replace('kansli', '').replace('arbetsförmedlingen', '').replace('arbets', '').replace('af ', '')

def similar_enough(abbreviation, full_name):
   """
   General-purpose function for matching the abbreviations used in the
   database to the full official names of the organisations
   """
   match = abbreviation == full_name
   if not match:
      match = (abbreviation == 'Enh Pers Distansmöte och Kontr' and full_name == 'Enheten It för personligt distansmöte och kontroll')
   if not match:
      match = (abbreviation == 'CIO Kansli' and full_name == 'Kansliet')
   if not match:
      match = (abbreviation == 'Enheten Eures' and full_name == 'Enheten Nationell samordning Eures')
   if not match:
      match = (abbreviation == 'Enh Tjänsteutveckling Leverantörer' and full_name == 'Enheten Tjänsteutveckling leverantör')
   if not match:
      match = (abbreviation == 'Enh Verksamhetsnära Stöd Ag As' and full_name == 'Enheten HR Verksamhetsnära stöd - VO Arbetsgivare och VO Arbetssökande')
   if not match:
      match = (abbreviation == 'Enh Kompetensförsörjning Ag-Stöd' and full_name == 'Enheten Kompetensförsörjning och arbetsgivarstöd')
   
   if not match:
      parts_1 = lengthen_common_abbreviations(remove_connectives(abbreviation.lower())).split()
      parts_2 = full_name.lower().replace('-', ' ').replace(',', ' ').replace('för ', '').replace('och', '').replace('vo', '').replace('arbets', '').split()


      # In many cases 'enheten' is missing for people in VO Direkt
      if parts_1[0] in ["göteborg", 'östersund', 'malmö', 'stockholm', 'södertälje', 'örebro', 'luleå']:
         parts_1 = ['enheten'] + parts_1

      if not match:
         match = compare_parts(parts_1, parts_2)

      # Try to catch the cases where 'enheten' has been dropped in the abbreviation
      if not match:
         for string in ['avdelningen', 'enheten', 'enheterna', 'avd', 'enh', 'direkt', 'sök', 'ag', 'hr']:
            if string in parts_1:
               parts_1.remove(string)
            if string in parts_2:
               parts_2.remove(string)
         match = compare_parts(parts_1, parts_2)
   return match

def similar_within_seek(abbreviation, full_name):
   """
   Function for matching the abbreviations used in the database to the
   full official names of the organisations, specifically within sök
   """
   match = abbreviation == full_name
   if not match:
      match = abbreviation == 'Sök Sunds Ånge Härnösand Timrå' and full_name == 'Enheten Södra Västernorrland'
   if not match:
      parts_1 = lengthen_abbreviations_specific_to_seek(lengthen_common_abbreviations(remove_connectives(abbreviation.replace('Sök ', '').lower()))).split()
      parts_2 = full_name.lower().replace('-', ' ').replace(',', ' ').replace('för ', '').replace('och', '').replace('vo', '').replace('arbets', '').replace('enheten', '').split()
      match = compare_parts(parts_1, parts_2)
   if not match:
      match = parts_1[0:3] == ['enheten', 'regionalt', 'stöd'] and parts_2[0] == 'region' and parts_1[3:] == parts_2[1:]
   return match
   
def similar_within_give(abbreviation, full_name):
   """
   Function for matching the abbreviations used in the database to the
   full official names of the organisations, specifically within AG
   """
   match = abbreviation == full_name
   if not match:
      match = (abbreviation == 'AG Beslut och Uppföljning Syd' and full_name == 'Enheten Beslut och uppföljning')
   if not match:
      match = (abbreviation == 'Enh Tjänsteutveckling Leverantörer' and full_name == 'Enheten Tjänsteutveckling leverantör')
   if not match:
      match = (abbreviation == 'AG Stockholm' and full_name == 'Enheten Stockholm stad')
   if not match:
      parts_1 = lengthen_abbreviations_specific_to_give(lengthen_common_abbreviations(remove_connectives(abbreviation.replace('AG ', '').lower()))).split()
      parts_2 = full_name.lower().replace('-', ' ').replace(',', ' ').replace('för ', '').replace('och', '').replace('vo', '').replace('arbets', '').replace('enheten', '').split()
      match = compare_parts(parts_1, parts_2)
   if not match:
      match = parts_1[0:3] == ['enheten', 'regionalt', 'stöd'] and parts_2[0] == 'region' and parts_1[-1] == parts_2[-1]
   return match

# note that this might select övrigt for things that are in sök or AG but not tied to a specific region
def find_VO(abbreviation):
   """
   Assumes the VO based on the initial word in an abbreviation from the
   global contact list. Note that this will sometimes pick 'other'
   - övrigt - even when the VO is actually sök or AG, but this is sorted
   out later.
   """
   parts = abbreviation.split()
   if parts[0] == 'Sök':
      VO = 'Arbetssökande'
   elif parts[0] == 'AG':
      VO = 'Arbetsgivare'
   else:
      VO = 'Övrigt'
   return VO

def find_match(abbreviation, keys, VO):
   """
   Using the abbreviation from the global contact list, attempts to figure
   out the official full name of the organisation
   """
   if VO == 'Övrigt':
      similarity_check = similar_enough
   elif VO == 'Arbetssökande':
      similarity_check = similar_within_seek
   elif VO == 'Arbetsgivare':
      similarity_check = similar_within_give
   match = None
   for full_name in keys:
      if similarity_check(abbreviation, full_name):
         match = full_name
         break
   return match

## Functions for reading and changing the contents of the Excel file

def read_and_clean(filename, verbose = False):
   df = pd.read_excel(filename, engine='openpyxl', dtype=str, sheet_name = 'Global_adresslista', header=0)

   expected_columns = ['ID', 'Förnamn', 'Efternamn', 'Titel', 'Företag', 'Avdelning', 'Kontor', 'Box', 'Adress', 'Stad', 'Region', 'Postnummer', 'Land/Region', 'Telefon', 'Mobiltelefon', 'Telefon (personsökare)', 'Telefon (bostad2)', 'Telefon (assistent)', 'Fax, arbete', 'Fax (hem)', 'Fax (annat)', 'Telexnummer', 'Visa namn', 'E-posttyp', 'E-postadress', 'Konto', 'Assistent', 'Skicka Rich Text', 'Primär', 'Normaliserat ämne']
   all_present = True
   missing_columns = []
   for col in expected_columns:
      col_present = col in df.columns
      all_present = all_present and col_present
      if not col_present:
         missing_columns.append(col)
   if not all_present:
      print("Columns present in file does not match the expected!")
      if verbose:
         print("Missing columns:")
         for col in missing_columns:
            print("\t{}".format(col))
      return

   if verbose:
      print("There are {} entries in total.".format(len(df)))
      print("Cleaning up everything that does not look like people...")
   narrowed = df[['Förnamn', 'Efternamn', 'Konto', 'Avdelning']].copy()
   no_nan = narrowed.dropna()
   if verbose:
      print("Dropped {} rows with NaN entries".format(len(narrowed) - len(no_nan)))
   no_dash = no_nan[no_nan['Avdelning'] != '-']
   if verbose:
      print("Dropped {} rows with dashes as Avdelning".format(len(no_nan) - len(no_dash)))
   cleaned = no_dash[no_dash['Konto'].str.len() == 5].copy()
   if verbose:
      print("Dropped {} rows with 'Konto' of length differing from five".format(len(no_dash) - len(cleaned)))
      print("There are now {} entries".format(len(cleaned)))
      print("\n")
      
   avdelningar = set(cleaned['Avdelning'])
   if verbose:
      print("There are {} unique 'avdelningar' represented in the original address list".format(len(set(df['Avdelning']))))
      print("Of these, {} remain after cleaning".format(len(avdelningar)))
      print("\n")

   cleaned.rename(columns = {'Avdelning': 'Avdelning enl. global kontaktlista'}, inplace = True)
   return cleaned

def find_organisational_position(cleaned):
   translations = []
   entry_supers = []
   entry_subs = []
   entry_subsubs = []
   for abbreviation in cleaned['Avdelning enl. global kontaktlista']:
      VO = find_VO(abbreviation)
      if VO == 'Arbetssökande':
         super_match = 'VO Arbetssökande'
         sub_match = find_match(abbreviation, sub_of_seek, VO)
         if sub_match != None:
            translations.append(sub_match)
            subsub_match = None
         else:
            subsub_match = find_match(abbreviation, subsub_to_sub[VO].keys(), VO)
            if subsub_match != None:
               translations.append(subsub_match)
               sub_match = subsub_to_sub[VO][subsub_match]
            else:
               translations.append('???')
               subsub_match = '???'
               sub_match = '???'
      elif VO == 'Arbetsgivare':
         super_match = 'VO Arbetsgivare'
         sub_match = find_match(abbreviation, sub_of_give, VO)
         if sub_match != None:
            translations.append(sub_match)
            subsub_match = None
         else:
            subsub_match = find_match(abbreviation, subsub_to_sub[VO].keys(), VO)
            if subsub_match != None:
               translations.append(subsub_match)
               sub_match = subsub_to_sub[VO][subsub_match]   
            else:
               translations.append('???')
               subsub_match = '???'
               sub_match = '???'
      elif VO == 'Övrigt':
         super_match = find_match(abbreviation, super_to_sub.keys(), VO)
         if super_match != None:
            translations.append(super_match)
            sub_match = None
         else:
            sub_match = find_match(abbreviation, sub_to_super.keys(), VO)
            if sub_match != None:
               translations.append(sub_match)
               subsub_match = None
            else:
               subsub_match = find_match(abbreviation, subsub_to_sub[VO].keys(), VO)
               if subsub_match != None:
                  translations.append(subsub_match)
                  sub_match = subsub_to_sub[VO][subsub_match]
               else:
                  translations.append('???')
                  subsub_match = '???'
                  sub_match = '???'
            super_match = sub_to_super[sub_match]
      entry_supers.append(super_match)
      entry_subs.append(sub_match)
      entry_subsubs.append(subsub_match)

   cleaned['Antagna avdelningsnamn'] = translations
   cleaned['Nivå 1'] = entry_supers
   cleaned['Nivå 2'] = entry_subs
   cleaned['Nivå 3'] = entry_subsubs
   return cleaned
   
def run(filename_in, filename_out, verbose = False):
   cleaned = read_and_clean(filename_in, verbose = verbose)
   if verbose:
      print('Finding organisational position...')
   find_organisational_position(cleaned)   
   cleaned.to_excel(filename_out, index = False)
   return
