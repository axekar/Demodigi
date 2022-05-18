"""
This module was written for the ESF-financed project Demokratisk
Digitalisering. The project is a collaboration between
Arbetsförmedlingen (AF) and Kungliga Tekniska Högskolan (KTH). The
purpose of the project is to increase the digital competence - as
defined at https://ec.europa.eu/jrc/en/digcomp - of people working at
Arbetsförmedlingen, and by extension also job seekers. This will be
done by learning modules at KTH using OLI-Torus.

--- About this Python module ---

This module is intended to read the tsv-files that come out of OLI-
TORUS, and transform them into json files that contain only the
information used by the factorial_experiment module.

Written by Alvin Gavel,

https://github.com/Alvin-Gavel/Demodigi
"""

import pandas as pd


def open_oli_results(filepath):
   df = pd.read_csv(filepath, sep='\t')
   return df
