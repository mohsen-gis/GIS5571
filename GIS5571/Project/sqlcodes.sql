population us county:

https://www.openintro.org/data/?data=county_complete

https://www.openintro.org/data/csv/county_complete.csv


Create table us_county_pop and import pop csv to the table 
-- Table: public.us_county_pop

-- DROP TABLE public.us_county_pop;

CREATE TABLE public.us_county_pop
(
    fips character varying(10) COLLATE pg_catalog."default",
    state_name character varying(100) COLLATE pg_catalog."default",
    county_name character varying(100) COLLATE pg_catalog."default",
    pop2017 character varying(15) COLLATE pg_catalog."default"
)

TABLESPACE pg_default;

ALTER TABLE public.us_county_pop
    OWNER to postgres;
    
    
# zero padding to the fips that are miising an initial 0

UPDATE us_county_pop
SET fips = concat(0,fips)
where length(fips)=4

# create a final county_pop table as follows: 

create table county_pop as(
select uc.geoid, uc.county_name, uc.state_name, ucp.pop2017, uc.geom
from us_county as uc left join us_county_pop as ucp on uc.geoid = ucp.fips
)

create table time_series as(
	SELECT s.geoid, s.county_name, s.state_name, c.date, coalesce(c.cases,0) as cases, coalesce(c.deaths,0) as deaths, s.pop2017
	FROM county_pop s 
	LEFT OUTER JOIN (SELECT date, cases, deaths, geoid FROM covid_county_data) c ON s.geoid = c.geoid
	)
    
    
# Delete null dates    
delete from time_series
where date is null

	create table daily_time_series as(
	with dataset as     (
     select
        geoid,
        county_name,
        state_name,
        date,
        cases,
        deaths,
        pop2017 as population
        
    from
        time_series    
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
		
		)
        
        
        
        #create monthly aggregation geodb
        
        
        create table covid_county_monthly_geom as(
		with temp1 as(
	SELECT date_part('year', date) as year, date_part('month', date) AS month, concat(date_part('year', date), '-', date_part('month', date)) as date,
	sum(new_cases)::int as monthly_cases, sum(new_deaths)::int as monthly_deaths, geoid, county_name, state_name, avg(population::int)::int as population
     FROM daily_time_series
 	GROUP BY year, month, geoid, state_name, county_name
			)
			select temp1.*, cp.geom
			from county_pop as cp right join temp1 on cp.geoid = temp1.geoid
 		)
        
        
        

# get rid of islands
        
        delete from covid_county_monthly_geom
where state_name = 'Puerto Rico'
   or state_name = 'United States Virgin Islands'
	 or state_name = 'Hawaii' 
	 or state_name = 'Alaska' 
	 or state_name = 'Commonwealth of the Northern Mariana Islands'
	 or state_name = 'Guam'
     or state_name = 'American Samoa'
        
    update county_pop
	set pop2017 = '2502'
	where geoid = '02275'
	
update county_pop
	set pop2017 = '1059'
	where geoid = '02230'
	
update county_pop
	set pop2017 = '2139'
	where geoid = '02105'
        
        
# build a full shapefile of monthly cases with 0s where not existed

with abol as(
		select * 
		from covid_county_monthly_geom
		where date = '2020-1'
		)
	 select coalesce(abol.date,'2020-1') as date, coalesce(abol.monthly_cases,0) as monthly_cases,  
			coalesce(abol.monthly_deaths,0) as monthly_deaths, coalesce(abol.geoid, cp.geoid) as geoid,
			coalesce(abol.county_name, cp.county_name) as county_name, coalesce(abol.state_name, cp.state_name) as state_name,
			coalesce(abol.population, cp.pop2017::int) as population
 from county_pop as cp left join abol on cp.geoid = abol.geoid



#Excel code
=IF(OR(H2="HH",H2="HL"),1,0)



