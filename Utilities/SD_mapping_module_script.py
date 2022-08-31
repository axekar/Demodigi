"""
This module is for importing data about the learning module kartläggning
"""

import SCB_data as sd

data = sd.SCB_data()
data.import_data('SCB_data/Kartläggning.csv')
data.connect_ID_and_code('dummy path')
data.export_data('SCB_data/Kartläggning_klar.csv')
