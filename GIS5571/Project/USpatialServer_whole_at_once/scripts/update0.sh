#!/bin/bash

# Exit the script of any statement returns a non-true return value. 
set -e

# Downlad county-level and state-level cumulative covid data
printf "%s\n***** Download the latest covid data from New York Times repo *****%s\n"

curl -o county_level/covid_county_data.csv https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv
curl -o state_level/covid_state_data.csv https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv
curl -o national_level/covid_nation_data.csv https://raw.githubusercontent.com/nytimes/covid-19-data/master/us.csv

# Load python program to upload latest covid data to covid_county_data and covid_state_data table
printf '%s\n**** Upload latest covid data to covid data tables *****%s\n'
python3 scripts/covid_data_table_update_v2.py


# Load sql file to update covid data to real_time_covid_data tables and insert covid data to time_series_covid_data table
printf '%s\n***** Update latest covid data to real-time tables *****'
printf '%s\n***** Insert latest covid data to timeseries tables *****'
#printf '%s\n***** Please input database information *****%s\n'

# read -p 'Database user: ' uservar
# read -p 'Database host: ' hostvar
# read -p 'Database: ' dbvar
#printf '%s\n*0*0*0*0* ACTION REQUIRED *0*0*0*0*%s\n'

export PGPASSWORD=haynes; psql -h 129.114.17.63 -U david -d solap_dev -W -f scripts/time_table_update.sql
#psql -h $hostvar -U $uservar -d $dbvar -W -f /Users/mohsen/Desktop/COVID19/COVID_mapping-master-final/data/archived_COVID_data/scripts/time_table_update.sql

#PGPASSWORD='haynes'; psql -h 129.114.17.63 -U david -d solap_dev -W -f /Users/mohsen/Desktop/COVID19/COVID_mapping-master-final/data/archived_COVID_data/scripts/grant.sql
# Load python script to update the hotspots' tables according to the new daily DB updates.
printf '%s\n**** Update the hotspot tables *****%s\n'
python3 scripts/lisa_copy.py

printf '%s\n***** Finish uploading *****%s\n'


