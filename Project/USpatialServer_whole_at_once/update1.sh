#!/bin/bash

# Exit the script of any statement returns a non-true return value. 
set -e

# Downlad county-level and state-level cumulative covid data
printf "%s\n***** Download the latest covid data from New York Times repo *****%s\n"
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )

curl -o "$parent_path"/csv_files/county_level/covid_county_data.csv https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv
curl -o "$parent_path"/csv_files/state_level/covid_state_data.csv https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv
curl -o "$parent_path"/csv_files/national_level/covid_nation_data.csv https://raw.githubusercontent.com/nytimes/covid-19-data/master/us.csv

# Load python program to upload latest covid data to covid_county_data and covid_state_data table
printf '%s\n**** Upload latest covid data to covid data tables *****%s\n'
python3 "$parent_path"/scripts/covid_data_table_update_v2.py


# Load sql file to update covid data to real_time_covid_data tables and insert covid data to time_series_covid_data table
printf '%s\n***** Update latest covid data to real-time and timeseries tables *****'

export PGPASSWORD=13651366; psql -h localhost -U postgres -d postgres -W -f "$parent_path"/scripts/time_table_update.sql

# Load python script to update the hotspots' tables according to the new daily DB updates.
printf '%s\n**** Update the hotspot tables *****%s\n'
# python3 "$parent_path"/scripts/lisa_copy.py

printf '%s\n***** Done! *****%s\n'

# For permission run: chmod +rx /Users/mohsen/Desktop/SummerRaProject/USpatialServer/update.sh
