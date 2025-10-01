Current Implementation for DEMO:

db_schema.py - Has two major operations create and drop.
Create makes all the tables and fills them with base values
Drop simply removes all the data from the database.

seeder.py - Creates csv files and an sql script file used
for initial seeding
must run generated sql file through command line to update
database.