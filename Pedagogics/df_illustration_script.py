"""
This is a script that uses the module differences to generate the plots
in the internal Demokratisk Digitalisering document "Statistisk analys
av kvalitetsskillnader".
"""

import differences as df

big_plot = False

df.compare_catapults(102, 98, 10, 10, 20)
df.compare_coins(0.6, 0.4, 20)
df.coin_long_run(0.6, 0.4, 20, 10000)

# Make sure you have a fast computer with lots of memory for this one.
if big_plot:
   df.catapult_long_run(102, 98, 10, 10, 20, 10000)
