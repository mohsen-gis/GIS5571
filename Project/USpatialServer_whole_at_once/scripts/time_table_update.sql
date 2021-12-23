-- 1. Update the date and covid date to real_time_covid_nation_data table

-- 4. Update the date and covid data to time_series_covid_nation_data table
-- INSERT INTO time_series_covid_nation_data (name, date, cases, deaths, population, geom) 
-- 	SELECT n.name, c.date::date, c.cases, c.deaths, n.population, n.geom
-- 	FROM us_nation n 
-- 	INNER JOIN (SELECT 'United States' as name, date, cases, deaths FROM covid_nation_data) c ON n.name = c.name;
-- -- Clean up the table
-- VACUUM ANALYZE time_series_covid_nation_data;

-- 5. Update the date and covid data to time_series_covid_state_data table
INSERT INTO time_series_covid_state_data (geoid, stusps, name, date, cases, deaths, population, geom) 
	SELECT s.geoid, s.stusps, s.name, c.date, coalesce(c.cases,0) as cases, coalesce(c.deaths,0) as deaths, s.population, s.geom
	FROM us_state s 
	LEFT OUTER JOIN (SELECT date, cases, deaths, geoid FROM covid_state_data) c ON s.geoid = c.geoid;
-- Clean up the table
VACUUM ANALYZE time_series_covid_state_data;

-- 6. Update the date and covid data to time_series_covid_county_data table
INSERT INTO time_series_covid_county_data (geoid, county_name, state_name, date, cases, deaths, population, geom) 
	SELECT s.geoid, s.county_name, s.state_name, c.date, coalesce(c.cases,0) as cases, coalesce(c.deaths,0) as deaths, s.population, s.geom
	FROM us_county s 
	LEFT OUTER JOIN (SELECT date, cases, deaths, geoid FROM covid_county_data) c ON s.geoid = c.geoid;
-- Clean up the table
VACUUM ANALYZE time_series_covid_county_data;