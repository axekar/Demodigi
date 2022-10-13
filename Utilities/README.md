This directory contains code written for some specific technical purpose, such as handling the data output by OLI Torus. Since it is of no scientific interest, it is stored separately from the other code.

The current contents of this directory are:

`README.md`: This text

`canvas_contact.py`: Module for interacting with the Canvas API, typically to provide individual feedback to the course participants

`extra_functions.py`: Module with useful little functions that do not fit anywhere else

`preprocessing.py`: Module for handling the data that comes out of OLI-Torus, changing it into a format suitable for the `factorial_experiment` module one level further up

`sensitive_data_management`: Module for handling person numbers and similar information

`canvas_user_script`: Script that creates the SIS datafile necessary to create users on Canvas.

`module_kickout_script`: Script for inactivating users on a module. Obviously, this is not a routine task and should only be used if you are sure that you know what you are doing.

`KL_user_script`: Script that does the routine work related to giving users access to the module `Kartläggning`

`KL_access_script`: Script for the routine task of renewing access to the module `Kartläggning` for users who have lost it for some reason

`KL_feedback_script`: Script that does the routine work related to giving feedback, for the module `Kartläggning`

`IS_user_script`: Script that does the routine work related to giving users access to the module `IT-säkerhet`

`IS_access_script`: Script for the routine task of renewing access to the module `IT-säkerhet` for users who have lost it for some reason


`Obsolete`: Directory containing code that we no longer expect to need

`Feedback_paragraphs`: Directory containing text files with the individual paragraphs that are combined when generating feedback to the individual users
