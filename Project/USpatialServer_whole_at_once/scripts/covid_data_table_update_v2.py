#! /usr/bin/python3

### Import modules
import os
import sqlalchemy
import pandas as pd
import datetime 
from glob import glob
from datetime import date, timedelta


#cur_path = os.getcwd()
#cur_path = os.path.dirname(__file__)
cur_path = os.path.abspath(__file__ + "/../../")

yesterday = date.today() - timedelta(days=1)

print("********** Input file paths and the date of yesterday **********")

county_path = cur_path + '/csv_files/county_level/covid_county_data.csv'
state_path = cur_path + '/csv_files/state_level/covid_state_data.csv'
nation_path = cur_path + '/csv_files/national_level/covid_nation_data.csv'
month = str(yesterday.month)
day = str(yesterday.day)
print('day is: ', day)
year = str(yesterday.year)


print("********** Input database info **********")
# user = 'ahmad178'
# password = 'student'
# host = '129.114.17.63'
# database = 'solap_dev'

user = 'postgres'
password = '13651366'
host = 'localhost'
database = 'postgres'

county_table = "covid_county_data"
state_table = "covid_state_data"
nation_table = "covid_nation_data"


database_info = {
    'user'           : user,
    'password'       : password,
    'host'           : host,
    'database'       : database,
    'county_table'   : county_table,
    'state_table'    : state_table,
    'nation_table'   : nation_table,
    }

engine = "postgresql://{user}:{password}@{host}/{database}".format(**database_info)

def nation_data_date(nation_path, month, day, year):
    """
    Function used to extract specific date data
    """
    print('IM in the nation function')
    nation_data_df = pd.read_csv(nation_path, parse_dates = ["date"])
    #month_new = int(month.lstrip("0"))
    #day_new = int(day.lstrip("0"))
    #print('day_new is', day_new )
    #year_new = int(year)

    nation_data_df_date = nation_data_df
    
    return nation_data_df_date

def state_data_date(state_path, month, day, year):
    """
    Function used to extract specific date data
    """
    print('IM in the state function')
    state_data_df = pd.read_csv(state_path, parse_dates = ["date"], dtype = {"fips":object})

    state_data_df_date = state_data_df
    state_data = state_data_df_date.rename(columns = {"state":"name", "fips":"geoid"})
    return state_data

def county_data_date(county_path, month, day, year):
    """
    Function used to extract specific date data
    """
    print('IM in the county function')
    county_data_df = pd.read_csv(county_path, parse_dates = ["date"], dtype = {"fips":object})

    county_data_df_date = county_data_df
    county_data_df_date.loc[county_data_df_date['county'] == 'New York City', 'fips'] = '36999'
    county_data_df_date.loc[county_data_df_date['county'] == 'Kansas City', 'fips'] = '29999'
    county_data = county_data_df_date.rename(columns = {"county":"county_name", "state":"state_name", "fips":"geoid"})
    return county_data

def data_to_sql(engine, nation_path, state_path, county_path, month, day, year):
    """
    Function used to append the curret date COVID data to county and state table
    """
    print('IM in the import to db function')
    try:
        eng = sqlalchemy.create_engine(engine)
    except sqlalchemy.exc.SQLAlchemyError as error:
        return error
    
    nation_data = nation_data_date(nation_path, month, day, year)
    state_data = state_data_date(state_path, month, day, year)
    county_data = county_data_date(county_path, month, day, year)

    if not nation_data.empty and not state_data.empty and not county_data.empty:
        nation_data.to_sql("{nation_table}".format(**database_info), if_exists = "append", con=eng, index=False)
        state_data.to_sql("{state_table}".format(**database_info), if_exists = "append", con=eng, index=False)
        county_data.to_sql("{county_table}".format(**database_info), if_exists = "append", con=eng, index=False)
        message = "Update {}-{}-{} COVID data to the {database}".format(month, day, year, **database_info)
        return message
    elif nation_data.empty:
        message = "Nation data for {}-{}-{} doesn't exist".format(month, day, year)
        return message
    elif state_data.empty:
        message = "State data for {}-{}-{} doesn't exist".format(month, day, year)
        return message
    elif county_data.empty:
         message = "County data for {}-{}-{} doesn't exist".format(month, day, year)
         return message

if __name__ == '__main__':
    print("****************************************")
    print(data_to_sql(engine, nation_path, state_path, county_path, month, day, year))








