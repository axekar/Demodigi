This directory contains code written for some specific technical purpose, such as automatically creating a SharePoint page. Since it is of no scientific interest, it is stored separately from the other code.

The current contents of this directory are:

`README.md`: This text

`account_info_generator.py`: Module for generating anonymous account IDs and easy to remember but hard to guess passwords

`AIG_run_script.py`: Script that runs the `account_info_generator` module on a csv-file of participant names and 5-character codes

`AIG_test_script.py`: Script for testing the `account_info_generator` module

`employees.py`: Module for figuring out the organisational positions of the employees at AF

`preprocessing.py`: Module for handling the data that comes out of OLI-Torus, changing it into a format suitable for the `factorial_experiment` module one level further up

`PP_mapping_module_script.py`: Script for handling the results of the course module `kartläggning`

`SCB_data.py`: Module for generating some of the data that will need to be delivered to Statistiska Centralbyrån (SCB)

`sharepoint_robot.py`: Module for creating SharePoint pages to share passwords with participants in the project

`Word_lists`: Directory containing lists of words to be used by the `account_info_generator.py` when generating user names and passwords
