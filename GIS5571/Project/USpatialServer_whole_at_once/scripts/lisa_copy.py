import datetime
from datetime import datetime as dt
from datetime import timedelta
startTime = datetime.datetime.now()
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 21 17:30:51 2020
Updated on Fri May 28 9:07 2020

David: I used geopandas as you can create a geospatial dataframe (in memory shapefile) 
Which can be connecte to PySAL. Very clean and neat

Mohsen: I used David's initial code to create and add to the DB 8 different hotspots tables for cumulative/daily at state/county level for deaths/incidence rates. 

@author: dahaynes, ahmad178
"""

# Mohsen's notes
# If (Image not found) error occurs, run this (for this specific machine): sudo ln -s /Library/Frameworks/Python.framework/Versions/3.8/lib/
# Pysal and Psycopg2 packages should be installed and upgraded in the base (root) environment so that the code could be successfully run in this env. 
errorContainer = []
import pysal, psycopg2, geopandas
from psycopg2 import extras
from sqlalchemy import create_engine
import psycopg2 
import io
import warnings
        
# a SQL query to fetch the required values to produce incidence statistic and pass it to the LISA analysis
# for hotspot detection of county disease cases

def parseQuery(query = None, isDate = None, delete = None):
    
    """
    This function parses SQL queries that are passed through the first argument (query), it also returns
    the last date in the clusters tables if the second argument (isDate) is not None. 
    It also clears the DB if the third argument (delete) is not None. 

    """
    
    global date1
    
    try:
        # connection = psycopg2.connect(user="ahmad178",
        #                               password="student",
        #                               host="129.114.17.63",
        #                               port="5432",
        #                               database="solap_dev")
        connection = psycopg2.connect(user="postgres",
                                      password="13651366",
                                      host="localhost",
                                      port="5432",
                                      database="postgres")
        cursor = connection.cursor()

        if delete is None:
            print('running the query')
            
            cursor.execute(query)
            print('Query is run successfully')
            if isDate is not None:
                print('retrieving the date')
                date1 = cursor.fetchall()
        
        else:
            print('clearing the DB')
            tablenames = ['temp_lisa_for_county_cases', 'temp_lisa_for_county_deaths', 'temp_lisa_for_state_cases', 'temp_lisa_for_state_deaths', 'temp_lisa_for_county_cases_with_geom_column', 'temp_lisa_for_county_deaths_with_geom_column', 'temp_lisa_for_state_cases_with_geom_column', 'temp_lisa_for_state_deaths_with_geom_column']
            
            for i in tablenames:
                drop_query = "DROP TABLE IF EXISTS {};".format(i)
                cursor.execute(drop_query) 
         
        connection.commit()
        cursor.close()
        connection.close()

    except (Exception, psycopg2.Error) as error :
        
        if str(type(error)) == "<class 'psycopg2.errors.UndefinedTable'>":
            print ("Error while updating the table in PostgreSQL:", error)
            date1 = []
        else:
            print ("Error while updating the table in PostgreSQL:", error)

    finally:
        #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")
            
def CreateTable(theDF, tableName):
    """

    Parameters
    ----------
    theDF : Pandas DataFrame
        DESCRIPTION

    Returns
    -------
    sqlStatement.

    """
    '''geoid, county_name, state_name, date, population, total_cases, new_cases, daily_incidence,lisa_daily,
        p_value_daily, quadrant_daily, category_daily, total_deaths, new_deaths, daily_death_rate,
        cum_death_rate, geom '''
        
    sqlStatement = "CREATE TABLE {} (".format(tableName)
    sqlDDL = []
    for colName, colType in zip(theDF.columns, theDF.dtypes):
        #print(colName, colType)
        if colType == 'object':
            colType = 'text'
        elif colType == 'float64':
            colType = 'double precision'
        elif colType == 'int32':
            colType = 'int'
        elif colName == 'total_cases' or colName == 'new_cases':
            colType == 'bigint'
        elif colName == 'geoid':
            colType == 'bigint'
        elif colName == 'record_date':    
            colType = 'date'
            colName = 'date'
        
        
        sqlDDL.append("{} {}".format(colName, colType))
    
    #print(sqlDDL)
    
    sqlStatement = "{} {} )".format(sqlStatement, ", ".join(sqlDDL)  )
    
    return(sqlStatement)

            
def fetch_variables_for_county_lisa():
    """
    Returns
    -------
    text string query

    """
    
    queryStatement = '''
      with dataset as     (
     select
        geoid,
        county_name,
        state_name,
        date,
        cases,
        deaths,
        population,
        geom     
    from
        time_series_covid_county_data     
    order by
        geoid,
        date     ), timelag as
        (
    select
        geoid,
        county_name,
        state_name,
        date,
        population,
        geom,
        cases as total_cases,
        cases-lag(cases,1)  over w as new_cases, 
        deaths as total_deaths,
        deaths-lag(deaths,1)  over w as new_deaths  
    from
        dataset     
    
    window w AS ( PARTITION BY
        geoid 
    order BY
        date )     )
    select
        geoid,
        county_name,
        state_name,
        date,
        population,
        geom as geometry,
        total_cases,
        coalesce(new_cases,0) as new_cases,
        round((coalesce(new_cases,0)*10000)/population::numeric,4) as daily_incidence,
        round((total_cases*10000)/population::numeric,4) as cum_incidence ,
        total_deaths,
        coalesce(new_deaths,0) as new_deaths,
        round(coalesce((new_deaths*100/total_cases),0)::numeric,4) as daily_death_rate,
        round((total_deaths*100/total_cases)::numeric,4) as cum_death_rate 
    
    from
        timelag     
    where
        total_cases >0
        '''.replace("\n","")
    
    return(queryStatement)
#where date_part('month', date) >= 5
# pulling data at state level
def fetch_variables_for_state_lisa():
    """
    Returns
    -------
    text string query

    """
    
    queryStatement = """
    with dataset as     (
    select
        geoid,
        county_name,
        state_name,
        date,
        cases,
        deaths,
        population,
        geom     
    from
        time_series_covid_county_data     
    order by
        geoid,
        date     ), timelag as      (
    select
        geoid,
        county_name,
        state_name,
        date,
        population,
        geom,
        cases as total_cases,
        coalesce(cases-lag(cases,1)  over w,0) as new_cases,
        coalesce(deaths-lag(deaths,1)  over w, 0) as new_deaths,
        deaths as total_deaths       
    from
        dataset     
   
    window w AS ( PARTITION BY
        geoid 
    order BY
        date )     ), oo as(
    select
        state_name,
        date,
        sum(total_cases) total_cases,
        sum(new_cases) new_cases,
        sum(total_deaths) total_deaths,
        sum(new_deaths) new_deaths       
    from
        timelag     
    where
        total_cases >0     
    group by
        date,
        state_name     
    order by
        state_name,
        date     ), joined as (
    select
        oo.*,
        us.population,
        us.geom as geometry     
    from
        oo 
    join
        us_state us 
            on (oo.state_name = us.name)     )
        select
            j.*,
            round((total_cases*10000/population),4) as cum_incidence,
            round((new_cases*10000/population),4) as daily_incidence,
            round((total_deaths*10000/population),4) as cum_death_rate,
            round((new_deaths*10000/population),4) as daily_death_rate      
    from
        joined j;
        
    """.replace("\n","")
    
    return(queryStatement)
# where date_part('month', date) >= 5 and date_part('day', date) >= 14

def ConnectDatabase(host, db, port, user, passwd):
    """
    This function creates the postgresql connection
    """
    connection = psycopg2.connect(host=host, database=db, port=port, user=user, password=passwd)
    cursor = connection.cursor(cursor_factory=extras.RealDictCursor)
    
    return connection, cursor



def import_to_DB(df, level):
    """
    This function appends the results of lisa analysis to temporary tables.
    -------
    The function expects 2 arguments, a data frame and the spatial level (e.g. state/county) and appends 
    to the corresponding teporary table. 

    """
    tableNames = {'county' : 'temp_lisa_for_county_cases', 'state' : 'temp_lisa_for_state_cases'}
    
    df['category_cum_copy'] = df['Category_cum']
    df['category_cum_deaths_copy'] = df['Category_cum_deaths']
    df['category_daily_copy'] = df['Category_daily']
    df['category_daily_deaths_copy'] = df['Category_daily_deaths']
    del df['Category_cum']
    del df['Category_cum_deaths']
    del df['Category_daily']
    del df['Category_daily_deaths']
    del df['geometry']  # deleting the geometry column to boost the program run-time. 
    
    # engine = create_engine('postgresql+psycopg2://ahmad178:student@129.114.17.63:5432/solap_dev')
    engine = create_engine('postgresql+psycopg2://postgres:13651366@localhost:5432/postgres')
    #importing data to table 'temp_lisa_for_county_cases'
    #if the table already exists (from previous loops over older dates) the data will be appended to the existed table
    df.head(0).to_sql(tableNames[level], engine, if_exists='append',index=False) 
    conn = engine.raw_connection()
    cur = conn.cursor()
    output = io.StringIO()
    df.to_csv(output, sep='\t', header=False, index=False)
    output.seek(0) #setting the file's current position at the offset; 0 means absolute file positioning
    contents = output.getvalue() # Retrieving file contents 
    cur.copy_from(output, tableNames[level], null = "") # null values become ''
    conn.commit() #committing the changes to the database
    conn.close()   
        
def create_final_layers_for_counties(): #disease hotspots at county level
    """
    This function adds a geometry column to the final temp_lisa_for_county_cases' tables 
    and creates two subsets of the data for daily and cumulative data where the confidence level is more than %95
    """

    join_query = '''
    create table temp_lisa_for_county_cases_with_geom_column as (
    with aa as(
    select
        h.*,
        u.statefp,
        u.geom     
    from
        temp_lisa_for_county_cases h 
    left join
        us_county u 
            on (h.geoid = u.geoid)     )
        select
            geoid,
            county_name,
            state_name,
            date,
            population,
            total_cases,
            new_cases,
            daily_incidence,
            cum_incidence,
            total_deaths,
            new_deaths,
            daily_death_rate,
            cum_death_rate,
            coalesce(lisa_cum, 0) as lisa_cum,
            p_value_cum,
            quadrant_cum,
            category_cum_copy as category_cum,
            coalesce(lisa_cum_deaths, 0) as lisa_cum_deaths,
            p_value_cum_deaths,
            quadrant_cum_deaths,
            category_cum_deaths_copy as category_cum_deaths,
            coalesce(lisa_daily, 0) as lisa_daily,
            coalesce(lisa_daily_deaths, 0) as lisa_daily_deaths,
            p_value_daily,
            quadrant_daily,
            category_daily_copy as category_daily,
            p_value_daily_deaths,
            quadrant_daily_deaths,
            category_daily_deaths_copy as category_daily_deaths,
            statefp,
            geom     
    from
        aa     );
    
    INSERT INTO daily_clusters_for_county_cases 
    select
        geoid,
        county_name,
        state_name,
        date,
        population,
        total_cases,
        new_cases,
        daily_incidence,
        lisa_daily,
        p_value_daily,
        quadrant_daily,
        category_daily,
        total_deaths,
        new_deaths,
        daily_death_rate,
        cum_death_rate,
        geom     
    from
        temp_lisa_for_county_cases_with_geom_column ;
   
    INSERT INTO cumulative_clusters_for_county_cases 
    select
        geoid,
        county_name,
        state_name,
        date,
        population,
        total_cases,
        new_cases,
        cum_incidence,
        lisa_cum,
        p_value_cum,
        quadrant_cum,
        category_cum,
        total_deaths,
        new_deaths,
        daily_death_rate,
        cum_death_rate,
        geom     
    from
        temp_lisa_for_county_cases_with_geom_column ;    

    INSERT INTO daily_clusters_for_county_deaths
    select
        geoid,
        county_name,
        state_name,
        date,
        population,
        total_cases,
        new_cases,
        daily_incidence,
        total_deaths,
        new_deaths,
        daily_death_rate,
        cum_death_rate,
        lisa_daily_deaths,
        p_value_daily_deaths,
        quadrant_daily_deaths,
        category_daily_deaths,
        geom     
    from
        temp_lisa_for_county_cases_with_geom_column;    
 
    INSERT INTO cumulative_clusters_for_county_deaths
    select
        geoid,
        county_name,
        state_name,
        date,
        population,
        total_cases,
        new_cases,
        daily_incidence,
        total_deaths,
        new_deaths,
        daily_death_rate,
        cum_death_rate,
        lisa_cum_deaths,
        p_value_cum_deaths,
        quadrant_cum_deaths,
        category_cum_deaths,
        geom     
    from
        temp_lisa_for_county_cases_with_geom_column ;    
    
    ''' 
    parseQuery(join_query)


def create_final_layers_for_states(): #disease hotspots at state level

    join_query = '''

    create table temp_lisa_for_state_cases_with_geom_column as (
    with aa as(
    select
        h.*,
        u.geom     
    from
        temp_lisa_for_state_cases h 
    left join
        us_state u 
            on (h.state_name = u.name)     )
        select
            state_name,
            date,
            total_cases,
            new_cases,
            total_deaths,
            new_deaths,
            population,
            cum_incidence,
            daily_incidence,
            cum_death_rate,
            daily_death_rate,
            coalesce(lisa_cum, 0) as lisa_cum,
            p_value_cum,
            quadrant_cum,
            coalesce(lisa_daily, 0) as lisa_daily,
            p_value_daily,
            quadrant_daily,
            category_cum_copy as category_cum,
            category_daily_copy as category_daily,
            coalesce(lisa_cum_deaths, 0) as lisa_cum_deaths,
            p_value_cum_deaths,
            quadrant_cum_deaths,
            coalesce(lisa_daily_deaths, 0) as lisa_daily_deaths,
            p_value_daily_deaths,
            quadrant_daily_deaths,
            category_cum_deaths_copy as category_cum_deaths,
            category_daily_deaths_copy as category_daily_deaths,
            geom     
    from
        aa     );
    INSERT INTO daily_clusters_for_state_cases 
    select
        state_name,
        date,
        total_cases,
        new_cases,
        daily_incidence,
        coalesce(lisa_daily, 0) as lisa_daily,
        p_value_daily,
        quadrant_daily,
        category_daily,
        total_deaths,
        new_deaths,
        daily_death_rate,
        cum_death_rate,
        geom     
    from
        temp_lisa_for_state_cases_with_geom_column ;

    INSERT INTO cumulative_clusters_for_state_cases
    select
        state_name,
        date,
        total_cases,
        new_cases,
        cum_incidence,
        coalesce(lisa_cum, 0) as lisa_cum,
        p_value_cum,
        quadrant_cum,
        category_cum,
        total_deaths,
        new_deaths,
        daily_death_rate,
        cum_death_rate,
        geom     
    from
        temp_lisa_for_state_cases_with_geom_column ;

    INSERT INTO daily_clusters_for_state_deaths
    select
        state_name,
        date,
        total_cases,
        new_cases,
        cum_incidence,
        total_deaths,
        new_deaths,
        daily_death_rate,
        cum_death_rate,
        coalesce(lisa_daily_deaths, 0) as lisa_daily_deaths,
        p_value_daily_deaths,
        quadrant_daily_deaths,
        category_daily_deaths,
        geom     
    from
        temp_lisa_for_state_cases_with_geom_column ;
    INSERT INTO cumulative_clusters_for_state_deaths
    select
        state_name,
        date,
        total_cases,
        new_cases,
        cum_incidence,
        total_deaths,
        new_deaths,
        daily_death_rate,
        cum_death_rate,
        coalesce(lisa_cum_deaths, 0) as lisa_cum_deaths,
        p_value_cum_deaths,
        quadrant_cum_deaths,
        category_cum_deaths,
        geom     
    from
        temp_lisa_for_state_cases_with_geom_column  ;   

    ''' 

    parseQuery(join_query)

def getPreviousDate(): 
    """
    This function gets the last available date (yesterday) of the clusters table in the DB. 
    """
    

    q = """
 
    select distinct date
    from daily_clusters_for_county_cases
    order by date desc


    """.replace("\n","")
    
    parseQuery(q, 'getThePreviousDate')

    return(date1)

# def main():

warnings.filterwarnings("ignore")
conn, cur = ConnectDatabase('localhost', 'postgres', 5432, 'postgres', '13651366')

# pulling data from the DB and storing it as a geopandas dataframe


#************Change this to be just pulling the data once
covidData_county = geopandas.GeoDataFrame.from_postgis(fetch_variables_for_county_lisa(), conn, geom_col='geometry') 
# covidData_state = geopandas.GeoDataFrame.from_postgis(fetch_variables_for_state_lisa(), conn, geom_col='geometry')

conn.close()

#Generate once per loop
dates = covidData_county["date"].unique()

parseQuery(None,None,'clearTheDB') #deleting outdated tables to avoid duplication when appending

myVariables = { "county": { 
            'cum_incidence':{'name':'cumulative county incidence','category':'cases','geog':'county', 'type':'cumulative'},
            'daily_incidence':{'name':'daily county incidence','category':'cases','geog':'county', 'type':'daily'},                           
            'cum_death_rate':{'name':'cumulative county mortality','category':'deaths','geog':'county', 'type':'cumulative'},
            'daily_death_rate':{'name':'daily county mortality','category':'deaths','geog':'county', 'type':'daily'}   
                }}
            # ,
            # "state" : {
            # 'cum_incidence':{'name':'cumulative state incidence','category':'cases','geog':'state', 'type':'cumulative'},
            # 'daily_incidence':{'name':'daily state incidence','category':'cases','geog':'state', 'type':'daily'},
            # 'cum_death_rate':{'name':'cumulative state mortality','category':'deaths','geog':'state', 'type':'cumulative'},
            # 'daily_death_rate':{'name':'daily state mortality','category':'deaths','geog':'state', 'type':'daily'}                    
            #     }  }                           
p1 = getPreviousDate()
p = str(p1).replace("[('",'').replace("',)]",'').replace("',)","").replace("('","")
if p1:
    pDate = p.split(', ')
    dates_list = [dt.strptime(date, '%Y-%m-%d').date() for date in pDate]
else:
    dates_list = []

flag = 'NO'
newdates = []
[any(newdates.append(d) for d in dates if d not in dates_list)]

for date in newdates:
        flag = 'YES'
        geoDF = covidData_county.loc[covidData_county["date"] == date]
        # geoDF_s = covidData_state.loc[covidData_state["date"] == date]
        levels = {'county' : geoDF} #, 'state' : geoDF_s}
        print("Analyzing {}".format(date))
        for i in levels.keys():
            weights = pysal.lib.weights.Queen.from_dataframe(levels[i])  #generates the weights' matrices with Queens strategy

            varss = {}
            varList = [*myVariables[i].keys()] #list of all variables for county lisa

            for j in varList: # loop over the variables
                # auto creation of local moran files with names starting with "lm_county_" or "lm_state_"
                globals()['lm_' + i + '_%s' % j] = pysal.explore.esda.Moran_Local(levels[i][j], weights, permutations=999)
                varss[j]=globals() ['lm_' + i + '_%s' % j]

            for recordName, recordValues in zip(['lisa_cum','p_value_cum', 'quadrant_cum','lisa_cum_deaths','p_value_cum_deaths', 'quadrant_cum_deaths','lisa_daily','p_value_daily', 'quadrant_daily', 'lisa_daily_deaths','p_value_daily_deaths', 'quadrant_daily_deaths'], [(varss[list(varss.keys())[0]]).Is, (varss[list(varss.keys())[0]]).p_sim, (varss[list(varss.keys())[0]]).q, (varss[list(varss.keys())[2]]).Is, (varss[list(varss.keys())[2]]).p_sim, (varss[list(varss.keys())[2]]).q, (varss[list(varss.keys())[1]]).Is, (varss[list(varss.keys())[1]]).p_sim, (varss[list(varss.keys())[1]]).q, (varss[list(varss.keys())[3]]).Is, (varss[list(varss.keys())[3]]).p_sim, (varss[list(varss.keys())[3]]).q]):
                levels[i].insert(len(levels[i].keys()), recordName, recordValues)

            categories = {1: "High-High", 2: "Low-High", 3: "Low-Low", 4: "High-Low"} #renaming the category values
            list1 = ['quadrant_cum', 'quadrant_cum_deaths', 'quadrant_daily', 'quadrant_daily_deaths']
            dict1 = {'quadrant_cum':"Category_cum", 'quadrant_cum_deaths':"Category_cum_deaths",'quadrant_daily':"Category_daily", 'quadrant_daily_deaths':"Category_daily_deaths"}
            for quad in categories:
                for j in list1:
                    levels[i].loc[(levels[i][j] == quad), dict1[j]] = categories[quad] #renaming the category values

            import_to_DB(levels[i],i)  #appending the resulting daily and cumulative cases clusters to the table temp_lisa_for_county_cases 

if flag == 'YES':
    #generating final layers    
    create_final_layers_for_counties() # adding geom column to the county cases clusters' table and creating the layers daily_clusters_for_county_cases and cumulative_clusters_for_county_cases
    # create_final_layers_for_states() # adding geom column to the state cases clusters' table and creating the layers daily_clusters_for_state_cases and cumulative_clusters_for_state_cases
    parseQuery(None,None,'clearTheDB')
endTime = datetime.datetime.now()
print("Finished")
print('runtime is ',endTime - startTime)

# if __name__ == '__main__':
#      main()




